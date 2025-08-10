from django.db import models

class ReservationStatus(models.TextChoices):
    PENDING    = 'PENDING', '대기'
    ACCEPTED   = 'ACCEPTED', '수락'
    REJECTED   = 'REJECTED', '거절'
    PREPARING  = 'PREPARING', '준비중'
    READY      = 'READY', '픽업준비완료'
    PICKED_UP  = 'PICKED_UP', '픽업완료'
    CANCELLED  = 'CANCELLED', '구매자취소'
    EXPIRED    = 'EXPIRED', '만료'

class RejectReason(models.TextChoices):
    OUT_OF_STOCK     = 'OUT_OF_STOCK', '재고 소진'
    CLOSED_TODAY     = 'CLOSED_TODAY', '금일 영업 종료'
    CLOSING_SOON     = 'CLOSING_SOON', '판매 시간 종료'
    TIME_UNAVAILABLE = 'TIME_UNAVAILABLE', '예약 시간 불가'
    TEMP_CLOSED      = 'TEMP_CLOSED', '일시적 휴무'
    FIELD_ISSUE      = 'FIELD_ISSUE', '날씨/현장상황'
    OTHER            = 'OTHER', '기타'

class Reservation(models.Model):
    # FK (users 앱 기준)
    store = models.ForeignKey('users.Store', on_delete=models.CASCADE, related_name='reservations')
    buyer = models.ForeignKey('users.Buyer', on_delete=models.CASCADE, related_name='reservations')

    # 요청 정보
    requested_pickup_at = models.DateTimeField(help_text='구매자가 희망한 픽업 시간')
    note = models.CharField(max_length=200, blank=True)

    # 상태/사유
    status = models.CharField(max_length=20, choices=ReservationStatus.choices, default=ReservationStatus.PENDING)
    rejected_reason = models.CharField(max_length=30, choices=RejectReason.choices, blank=True)
    rejected_reason_detail = models.CharField(max_length=200, blank=True)
    cancelled_reason = models.CharField(max_length=200, blank=True)

    # 타임스탬프 (뷰에서 필요 시 채움)
    accepted_at = models.DateTimeField(null=True, blank=True)
    prepared_at = models.DateTimeField(null=True, blank=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 금액 스냅샷
    total_price = models.PositiveIntegerField(default=0, help_text='예약 시점 총액(원)')

    # 카드 표시용 스냅샷
    contact_phone = models.CharField(max_length=20, blank=True)
    display_image = models.ImageField(upload_to='reservations/cover/%Y/%m/%d/', blank=True)

    # 픽업 검증 코드
    reservation_code = models.CharField(max_length=12, unique=True, blank=True)

    # 판매자 메모/ETA
    seller_note = models.CharField(max_length=200, blank=True)
    prep_eta_minutes = models.PositiveSmallIntegerField(default=0, help_text='준비 예상 소요 분')

    # 리워드 지급 여부
    point_rewarded = models.BooleanField(default=False)

    # (선택) 픽업 윈도우
    pickup_window_start = models.DateTimeField(null=True, blank=True)
    pickup_window_end   = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['store', 'status']),
            models.Index(fields=['buyer', 'status']),
            models.Index(fields=['requested_pickup_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.get_status_display()}] {self.store.name} - {self.buyer.user.username}'

    # 최소 동작만 유지: 최초 생성 시 코드 발급
    def save(self, *args, **kwargs):
        if not self.pk and not self.reservation_code:
            import secrets, string
            alphabet = string.ascii_uppercase + string.digits
            self.reservation_code = ''.join(secrets.choice(alphabet) for _ in range(8))
        super().save(*args, **kwargs)

class ReservationItem(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=100)
    unit_price = models.PositiveIntegerField(help_text='개당 가격(원, 스냅샷)')
    quantity = models.PositiveIntegerField(default=1)
    unit = models.CharField(max_length=20, blank=True, help_text='단위(봉, 단, kg 등)')
    memo = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='reservations/items/%Y/%m/%d/', blank=True)

    def __str__(self):
        return f'{self.item_name} x {self.quantity}'

    # 최소 동작만 유지: 합계 갱신
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        total = sum(i.unit_price * i.quantity for i in self.reservation.items.all())
        Reservation.objects.filter(pk=self.reservation_id).update(total_price=total)
