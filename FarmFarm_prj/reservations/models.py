import secrets
import string
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import F, IntegerField, Sum, ExpressionWrapper, CheckConstraint, Q
from django.conf import settings

# users.models에서 UserType을 가져온다고 가정합니다.
# 실제 프로젝트 구조에 맞게 경로를 수정해주세요.
from users.models import UserType 

class ReservationStatus(models.TextChoices):
    PENDING   = 'PENDING', '대기'
    ACCEPTED  = 'ACCEPTED', '수락'
    REJECTED  = 'REJECTED', '거절'
    PREPARING = 'PREPARING', '준비중'
    READY     = 'READY', '픽업준비완료'
    PICKED_UP = 'PICKED_UP', '픽업완료'
    CANCELLED = 'CANCELLED', '구매자취소'
    EXPIRED   = 'EXPIRED', '만료'

class RejectReason(models.TextChoices):
    OUT_OF_STOCK     = 'OUT_OF_STOCK', '재고 소진'
    CLOSED_TODAY     = 'CLOSED_TODAY', '금일 영업 종료'
    CLOSING_SOON     = 'CLOSING_SOON', '판매 시간 종료'
    TIME_UNAVAILABLE = 'TIME_UNAVAILABLE', '예약 시간 불가'
    TEMP_CLOSED      = 'TEMP_CLOSED', '일시적 휴무'
    FIELD_ISSUE      = 'FIELD_ISSUE', '날씨/현장상황'
    OTHER            = 'OTHER', '기타'

class Reservation(models.Model):
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='reservations')
    buyer = models.ForeignKey('users.Buyer', on_delete=models.CASCADE, related_name='reservations') 

    requested_pickup_at = models.DateTimeField(help_text='구매자가 희망한 픽업 시간')
    note = models.CharField(max_length=200, blank=True)

    status = models.CharField(max_length=20, choices=ReservationStatus.choices, default=ReservationStatus.PENDING)
    rejected_reason = models.CharField(max_length=30, choices=RejectReason.choices, blank=True)
    # rejected_reason_detail 필드를 제거했습니다.
    cancelled_reason = models.CharField(max_length=200, blank=True)

    accepted_at = models.DateTimeField(null=True, blank=True)
    prepared_at = models.DateTimeField(null=True, blank=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    total_price = models.PositiveIntegerField(default=0, help_text='예약 시점 총액(원)')
    contact_phone = models.CharField(max_length=20, blank=True)
    display_image = models.ImageField(upload_to='reservations/cover/%Y/%m/%d/', blank=True)
    reservation_code = models.CharField(max_length=12, unique=True, db_index=True, blank=True)
    seller_note = models.CharField(max_length=200, blank=True)
    prep_eta_minutes = models.PositiveSmallIntegerField(default=0, help_text='준비 예상 소요 분')
    pickup_window_start = models.DateTimeField(null=True, blank=True)
    pickup_window_end   = models.DateTimeField(null=True, blank=True)
    point_rewarded = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['store', 'status']),
            models.Index(fields=['buyer', 'status']),
            models.Index(fields=['requested_pickup_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.get_status_display()}] {self.store} - {self.buyer}'

    def clean(self):
        if self.requested_pickup_at and self.requested_pickup_at < timezone.now():
            raise ValidationError('과거 시간으로는 예약할 수 없습니다.')
        if self.pickup_window_start and self.pickup_window_end:
            if self.pickup_window_end <= self.pickup_window_start:
                raise ValidationError('픽업 윈도우 시간이 올바르지 않습니다.')

    def save(self, *args, **kwargs):
        if not self.pk and not self.reservation_code:
            alphabet = string.ascii_uppercase + string.digits
            self.reservation_code = ''.join(secrets.choice(alphabet) for _ in range(8))
        super().save(*args, **kwargs)

    def recompute_total(self):
        total = self.items.aggregate(
            s=Sum(ExpressionWrapper(F('unit_price') * F('quantity'), output_field=IntegerField()))
        )['s'] or 0
        if total != self.total_price:
            self.total_price = total
            self.save(update_fields=['total_price'])

    # --- 비즈니스 로직 메서드 ---
    
    def can_transition_to(self, new_status, user):
        """사용자와 목표 상태를 기반으로 상태 변경이 가능한지 확인"""
        if not user.is_authenticated:
            return False
            
        if user.usertype == UserType.BUYER and self.buyer.user_id == user.id:
            allowed = {
                ReservationStatus.PENDING: {ReservationStatus.CANCELLED},
                ReservationStatus.ACCEPTED: {ReservationStatus.CANCELLED, ReservationStatus.PICKED_UP},
                ReservationStatus.PREPARING: {ReservationStatus.PICKED_UP},
                ReservationStatus.READY: {ReservationStatus.PICKED_UP},
            }
            return self.status in allowed and new_status in allowed.get(self.status, set())
        
        elif user.usertype == UserType.SELLER and self.store.seller.user_id == user.id:
            allowed = {
                ReservationStatus.PENDING: {ReservationStatus.ACCEPTED, ReservationStatus.REJECTED},
                ReservationStatus.ACCEPTED: {ReservationStatus.PREPARING, ReservationStatus.REJECTED},
                ReservationStatus.PREPARING: {ReservationStatus.READY},
            }
            return self.status in allowed and new_status in allowed.get(self.status, set())
        
        return False

    def update_status(self, new_status):
        """상태를 변경하고 시간을 기록"""
        self.status = new_status
        now = timezone.now()
        ts_map = {
            ReservationStatus.ACCEPTED: 'accepted_at',
            ReservationStatus.PREPARING: 'prepared_at',
            ReservationStatus.READY: 'ready_at',
            ReservationStatus.PICKED_UP: 'picked_up_at',
            ReservationStatus.CANCELLED: 'cancelled_at',
        }
        update_fields = ['status']
        if new_status in ts_map:
            setattr(self, ts_map[new_status], now)
            update_fields.append(ts_map[new_status])
        self.save(update_fields=update_fields)

    def reject(self, reason):
        """예약을 거절하고 사유를 기록"""
        self.status = ReservationStatus.REJECTED
        self.rejected_reason = reason
        self.rejected_at = timezone.now()
        self.save(update_fields=['status', 'rejected_reason', 'rejected_at'])


class ReservationItem(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=100)
    unit_price = models.PositiveIntegerField(help_text='개당 가격(원, 스냅샷)')
    quantity = models.PositiveIntegerField(default=1)
    unit = models.CharField(max_length=20, blank=True, help_text='단위(봉, 단, kg 등)')
    memo = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='reservations/items/%Y/%m/%d/', blank=True)
    
    original_item = models.ForeignKey(
        'items.Item', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reservation_items'
    )

    class Meta:
        constraints = [
            CheckConstraint(check=Q(quantity__gte=1), name='quantity_gte_1'),
            CheckConstraint(check=Q(unit_price__gte=0), name='unit_price_gte_0'),
        ]

    def __str__(self):
        return f'{self.item_name} x {self.quantity}'

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new or 'quantity' in kwargs.get('update_fields', []):
            self.reservation.recompute_total()
