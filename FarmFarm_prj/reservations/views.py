from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Reservation, ReservationItem, ReservationStatus
from users.models import UserType # ★ users 모델 사용
from stores.models import Store
from django.core.paginator import Paginator
from django.db.models import Q
from users.models import UserType
from django.contrib.auth.decorators import login_required
from datetime import datetime

# 공통 헬퍼: 로그인 & 역할 검사
def _require_buyer(request):
    if not request.user.is_authenticated:
        messages.error(request, '로그인이 필요합니다.')
        return None, redirect('users:login')
    if request.user.usertype != UserType.BUYER or not hasattr(request.user, 'buyer'):
        messages.error(request, '구매자만 이용할 수 있습니다.')
        return None, redirect('users:onboarding')
    return request.user.buyer, None

def _require_seller(request):
    if not request.user.is_authenticated:
        messages.error(request, '로그인이 필요합니다.')
        return None, redirect('users:login')
    if request.user.usertype != UserType.SELLER or not hasattr(request.user, 'seller'):
        messages.error(request, '판매자만 이용할 수 있습니다.')
        return None, redirect('users:onboarding')
    return request.user.seller, None

@login_required
def reservation_list(request):
    """구매자 내 예약 목록"""
    buyer, jump = _require_buyer(request)
    if jump: return jump

    qs = (Reservation.objects
          .filter(buyer=buyer)
          .select_related('store')
          .prefetch_related('items'))
    return render(request, 'reservations/reservation_list.html', {
        'reservations': qs,
        'now': timezone.now(),
    })

@login_required
def reservation_create_form(request):
    """예약 생성 폼 (구매자 전용)"""
    buyer, jump = _require_buyer(request)
    if jump: return jump

    stores = Store.objects.all()[:50]
    return render(request, 'reservations/reservation_create.html', {
        'stores': stores,
        'min_time': timezone.now().strftime('%Y-%m-%dT%H:%M'),
    })


@require_http_methods(["POST"])
@login_required
@transaction.atomic
def reservation_create(request):
    # 0) 로그인/역할 확인
    buyer, jump = _require_buyer(request)
    if jump:
        return jump

    # 1) 값 꺼내기 + 공백 제거
    store_id      = (request.POST.get('store_id') or '').strip()
    pickup_time   = (request.POST.get('pickup_time') or '').strip()   # 'HH:MM'
    note          = (request.POST.get('note') or '').strip()
    item_name     = (request.POST.get('item_name') or '').strip()
    unit_price_s  = (request.POST.get('unit_price') or '').strip()
    quantity_s    = (request.POST.get('quantity') or '').strip()
    unit          = (request.POST.get('unit') or '').strip()

    # 2) store_id 검증
    if not store_id.isdigit():
        messages.error(request, '가게를 선택해 주세요.')
        return redirect('reservations:create_form')
    store = get_object_or_404(Store, pk=int(store_id))

    # 3) 도착시간 검증/변환 (오늘 날짜 + 선택 시간)
    if not pickup_time:
        messages.error(request, '도착 시간을 선택해 주세요.')
        return redirect('reservations:create_form')
    try:
        hh, mm = map(int, pickup_time.split(':', 1))
        today = timezone.localdate()
        naive_dt = datetime(today.year, today.month, today.day, hh, mm)
        requested_pickup_at = timezone.make_aware(naive_dt, timezone.get_current_timezone())
    except Exception:
        messages.error(request, '도착 시간 형식이 올바르지 않습니다.')
        return redirect('reservations:create_form')
    if requested_pickup_at < timezone.now():
        messages.error(request, '지나간 시간으로 예약할 수 없습니다.')
        return redirect('reservations:create_form')

    # 4) 수량/가격 검증
    try:
        quantity = max(1, int(quantity_s))
    except ValueError:
        messages.error(request, '수량은 1 이상의 숫자여야 합니다.')
        return redirect('reservations:create_form')

    try:
        unit_price = int(unit_price_s)
        if unit_price < 0:
            raise ValueError
    except ValueError:
        messages.error(request, '가격 형식이 올바르지 않습니다.')
        return redirect('reservations:create_form')

    if not item_name:
        item_name = '상품'

    # 5) 예약 생성
    r = Reservation.objects.create(
        store=store,
        buyer=buyer,
        requested_pickup_at=requested_pickup_at,
        note=note,
        contact_phone=getattr(store, 'phone', ''),
        point_rewarded=False,  # 모델 기본값이 있어도 안전하게 명시
    )

    # 6) 아이템 생성 (수량 + 가격만 사용)
    ReservationItem.objects.create(
        reservation=r,
        item_name=item_name,
        unit_price=unit_price,
        quantity=quantity,
        unit=unit,
    )

    # 7) 총액 갱신 + 완료
    r.recompute_total()
    messages.success(request, '예약이 생성되었습니다.')
    return redirect('reservations:list')

@require_http_methods(["POST"])
@login_required
def reservation_change_status(request, pk):
    """
    상태 변경:
    - 구매자: 자기 예약만 CANCELLED/PICKED_UP 변경 허용(데모 기준)
    - 판매자: 자기 가게 예약만 ACCEPTED/PREPARING/READY/PICKED_UP/REJECTED 허용
    """
    r = get_object_or_404(Reservation, pk=pk)
    to_status = request.POST.get('to_status')

    # 공통: 상태 값 검증
    valid_status_keys = {k for k, _ in ReservationStatus.choices}
    if to_status not in valid_status_keys:
        messages.error(request, '잘못된 상태입니다.')
        return redirect('reservations:list')

    now = timezone.now()
    ts_map = {
        ReservationStatus.ACCEPTED: 'accepted_at',
        ReservationStatus.PREPARING: 'prepared_at',
        ReservationStatus.READY: 'ready_at',
        ReservationStatus.PICKED_UP: 'picked_up_at',
        ReservationStatus.REJECTED: 'rejected_at',
        ReservationStatus.CANCELLED: 'cancelled_at',
    }

    # 권한/소유 검증 + 전이 규칙
    if request.user.usertype == UserType.BUYER and hasattr(request.user, 'buyer'):
        if r.buyer_id != request.user.buyer.id:
            messages.error(request, '내 예약만 변경할 수 있어요.')
            return redirect('reservations:list')
        allowed = {
            ReservationStatus.PENDING: {ReservationStatus.CANCELLED},
            ReservationStatus.ACCEPTED: {ReservationStatus.CANCELLED},
            ReservationStatus.READY: {ReservationStatus.PICKED_UP},  # 구매자 측 완료 체크
        }
    elif request.user.usertype == UserType.SELLER and hasattr(request.user, 'seller'):
        # 판매자: 본인 가게 소유 확인
        if r.store and hasattr(request.user.seller, 'store'):
            if r.store_id != request.user.seller.store_id:
                messages.error(request, '내 가게의 예약만 변경할 수 있어요.')
                return redirect('users:seller_home')
        # 데모 전이
        allowed = {
            ReservationStatus.PENDING: {ReservationStatus.ACCEPTED, ReservationStatus.REJECTED},
            ReservationStatus.ACCEPTED: {ReservationStatus.PREPARING, ReservationStatus.REJECTED},
            ReservationStatus.PREPARING: {ReservationStatus.READY},
            ReservationStatus.READY: {ReservationStatus.PICKED_UP},
        }
    else:
        messages.error(request, '권한이 없습니다.')
        return redirect('users:onboarding')

    if r.status in allowed and to_status in allowed[r.status]:
        r.status = to_status
        field = ts_map.get(to_status)
        if field:
            setattr(r, field, now)
        r.full_clean()
        r.save()
        messages.success(request, f'상태가 {r.get_status_display()}로 변경되었습니다.')
    else:
        messages.error(request, '허용되지 않는 상태 전이입니다.')

    # 구매자는 리스트로, 판매자는 홈으로 돌려보내기(원하면 분리 라우팅)
    return redirect('reservations:list' if request.user.usertype == UserType.BUYER else 'users:seller_home')

@login_required
def seller_reservation_list(request):
    if request.user.usertype != UserType.SELLER or not hasattr(request.user, 'seller'):
        messages.error(request, '판매자만 접근할 수 있습니다.')
        return redirect('users:onboarding')

    seller = request.user.seller

    # TODO: 프로젝트 실제 필드명에 맞춰 소유 가게 가져오기
    # ex1) Seller가 store를 1:1로 가진다면:
    store = getattr(seller, 'store', None)

    # ex2) Store에 owner=Seller FK가 있다면:
    # stores = Store.objects.filter(owner=seller)
    # (아래에서 store 대신 stores 사용)

    qs = Reservation.objects.none()
    if store:
        qs = (Reservation.objects
              .filter(store=store)
              .select_related('buyer__user')
              .prefetch_related('items')
              .order_by('-created_at'))

    # ★ 리다이렉트하지 말고 그냥 빈 목록/안내 메시지로 렌더
    if not store:
        messages.info(request, '아직 연결된 가게가 없어요. 가게를 등록해 주세요!')

    return render(request, 'reservations/seller_list.html', {
        'store': store,            # 없어도 None으로 템플릿에 전달
        'page_obj': qs,            # 페이지네이션 안 쓰면 qs 그대로
        'status_now': '',
        'q': '',
        'date': '',
        'status_choices': ReservationStatus.choices,
    })