import json
from django.http import JsonResponse
from django.db import transaction
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Reservation, ReservationItem, ReservationStatus
from .forms import ReservationForm, ReservationItemForm, SellerReservationUpdateForm
from users.models import UserType
from stores.models import Store, StoreItem
from items.models import Item   
from reviews.forms import ReviewForm

# ... _require_buyer, _require_seller 등 헬퍼 함수 ...



@require_http_methods(["GET"])
def get_store_items_api(request, store_id):
    """API: 특정 가게의 판매 상품 목록을 JSON으로 반환 (StoreItem 기준, 가게 정보 포함)"""
    store = get_object_or_404(Store, pk=store_id)
    store_items = store.store_items.select_related('item').all()
    
    items_data = [{
        'id': store_item.id,
        'name': store_item.item.name,
        'price': store_item.price,
        'unit': store_item.unit,
        'description': store_item.description,
        'photo_url': store_item.photo.url if store_item.photo else 'https://placehold.co/200x150?text=No+Image',
        'sale_hours': store.sale_hours,
        'address': store.address,
    } for store_item in store_items]
    
    return JsonResponse({'items': items_data})

@require_http_methods(["POST"])
@login_required
@transaction.atomic
def reservation_create_api(request):
    """API: JSON 데이터를 받아 예약을 생성 (수정된 버전)"""
    buyer, jump = _require_buyer(request)
    if jump: return JsonResponse({'error': '권한이 없습니다.'}, status=403)

    try:
        data = json.loads(request.body)
        # JavaScript가 보내주는 item_id는 사실 StoreItem의 id 입니다.
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
        pickup_time_str = data.get('pickup_time')
        
        # ★★★ 핵심 수정점 1: Item 대신 StoreItem을 조회합니다. ★★★
        store_item = get_object_or_404(StoreItem, pk=item_id)
        
        hh, mm = map(int, pickup_time_str.split(':'))
        today = timezone.localdate()
        requested_pickup_at = timezone.make_aware(datetime(today.year, today.month, today.day, hh, mm))

        if requested_pickup_at < timezone.now():
            return JsonResponse({'error': '과거 시간으로 예약할 수 없습니다.'}, status=400)

        # ★★★ 핵심 수정점 2: store_item 객체에서 가게 정보를 가져옵니다. ★★★
        reservation = Reservation.objects.create(
            store=store_item.store,
            buyer=buyer,
            requested_pickup_at=requested_pickup_at,
        )
        
        # ★★★ 핵심 수정점 3: store_item 객체에서 상품 정보를 가져옵니다. ★★★
        ReservationItem.objects.create(
            reservation=reservation,
            item_name=store_item.item.name, # 실제 이름은 store_item.item.name
            unit_price=store_item.price,      # 가격은 store_item.price
            quantity=quantity,
            unit=store_item.unit,           # 단위는 store_item.unit
            original_item=store_item.item,    # 원본 Item 연결
            image=store_item.photo,
        )
        
        return JsonResponse({'message': '예약이 성공적으로 생성되었습니다.', 'reservation_id': reservation.id})

    except Exception as e:
        return JsonResponse({'error': f'잘못된 요청입니다: {e}'}, status=400)

# 공통 헬퍼: 로그인 & 역할 검사 (기존 코드 유지)
def _require_buyer(request):
    if not request.user.is_authenticated or request.user.usertype != UserType.BUYER or not hasattr(request.user, 'buyer'):
        messages.error(request, '구매자만 이용할 수 있습니다.')
        return None, redirect('users:login') # 혹은 적절한 페이지로
    return request.user.buyer, None

def _require_seller(request):
    if not request.user.is_authenticated or request.user.usertype != UserType.SELLER or not hasattr(request.user, 'seller'):
        messages.error(request, '판매자만 이용할 수 있습니다.')
        return None, redirect('users:login') # 혹은 적절한 페이지로
    return request.user.seller, None


@login_required
def reservation_list(request):
    """구매자: 내 예약 목록"""
    buyer, jump = _require_buyer(request)
    if jump: 
        return jump

    reservation_list = (Reservation.objects
        .filter(buyer=buyer)
        .select_related('store')
        .prefetch_related('items')
        .order_by('-created_at'))
    
    now = timezone.now()
    for r in reservation_list:
        # ACCEPTED 상태일 때만 남은 시간 계산
        if r.status == 'ACCEPTED' and r.requested_pickup_at:
            diff = r.requested_pickup_at - now
            r.remaining_minutes = int(diff.total_seconds() // 60)
            if r.remaining_minutes < 0:
                r.remaining_minutes = 0
        else:
            r.remaining_minutes = None  # 나머지는 None 처리
    
    review_form = ReviewForm()
    return render(request, 'reservations/reservation_list.html', {
        'reservations': reservation_list,
        'review_form': review_form,
        'now': now,
    })


@login_required
def reservation_create_view(request):
    """구매자: 예약 생성 (폼 + 처리)"""
    buyer, jump = _require_buyer(request)
    if jump: return jump

    if request.method == 'POST':
        # 실제로는 여러 아이템을 받을 수 있도록 FormSet을 사용하는 것이 이상적입니다.
        # 여기서는 데모를 위해 단일 아이템만 처리합니다.
        reservation_form = ReservationForm(request.POST)
        item_form = ReservationItemForm(request.POST)

        if reservation_form.is_valid() and item_form.is_valid():
            with transaction.atomic():
                reservation = reservation_form.save(commit=False)
                reservation.buyer = buyer
                reservation.save()

                item = item_form.save(commit=False)
                item.reservation = reservation
                item.save()

                # recompute_total은 ReservationItem.save()에서 호출되므로 여기서 또 호출할 필요 없음
            
            messages.success(request, '예약이 성공적으로 생성되었습니다.')
            return redirect('reservations:list')
        else:
            messages.error(request, '입력 내용을 다시 확인해주세요.')
    else:
        reservation_form = ReservationForm()
        item_form = ReservationItemForm()

    return render(request, 'reservations/reservation_form.html', {
        'reservation_form': reservation_form,
        'item_form': item_form,
        'stores': Store.objects.all()[:50] # 예시: 활성화된 가게만 필터링하는 로직은 stores 앱에서 별도 구현 필요
    })

@require_http_methods(["POST"])
@login_required
def reservation_change_status(request, pk):
    """판매자/구매자: 예약 상태 변경 (AJAX 확인 로직 최종 수정)"""
    reservation = get_object_or_404(Reservation, pk=pk)
    
    # ★★★ 핵심 수정점: AJAX 요청을 더 확실하게 감지합니다. ★★★
    # JavaScript의 fetch는 보통 FormData나 JSON으로 데이터를 보냅니다.
    # 'X-Requested-With' 헤더는 jQuery 등 특정 라이브러리만 보내므로,
    # 이 헤더의 유무로만 판단하는 것은 불안정합니다.
    # 여기서는 'AJAX 요청일 것이다'라고 폭넓게 가정하고 JSON으로 응답하는 것이
    # 현재 프론트엔드 코드와 호환됩니다.
    is_ajax_request = True # 우선 AJAX 요청이라고 가정

    to_status = request.POST.get('to_status')
    redirect_url = 'reservations:list' if request.user.usertype == UserType.BUYER else 'reservations:seller_list'

    if not reservation.can_transition_to(to_status, request.user):
        message = '허용되지 않는 요청이거나 권한이 없습니다.'
        if is_ajax_request:
            return JsonResponse({'status': 'error', 'message': message}, status=403)
        messages.error(request, message)
        return redirect(redirect_url)

    try:
        if to_status == ReservationStatus.REJECTED:
            form = SellerReservationUpdateForm(request.POST, instance=reservation)
            if form.is_valid():
                reservation.reject(reason=form.cleaned_data.get('rejected_reason'))
            else:
                raise ValueError('거절 사유를 올바르게 입력해주세요.')
        else:
            reservation.update_status(to_status)

        message = f'상태가 {reservation.get_status_display()}(으)로 변경되었습니다.'
        
        # AJAX 요청이면 항상 JSON으로 응답합니다.
        if is_ajax_request:
            return JsonResponse({
                'status': 'success',
                'message': message,
                'new_status': reservation.get_status_display()
            })
        
        # AJAX가 아닐 경우에만 메시지와 함께 리디렉션합니다.
        messages.success(request, message)
        return redirect(redirect_url)

    except ValueError as e:
        message = str(e)
        if is_ajax_request:
            return JsonResponse({'status': 'error', 'message': message}, status=400)
        messages.error(request, message)
        return redirect(redirect_url)


@login_required
def seller_reservation_list(request):
    """판매자: 내 가게 예약 목록 (거절 모달 폼 추가)"""
    seller, jump = _require_seller(request)
    if jump: return jump

    stores_owned_by_seller = Store.objects.filter(seller=seller)
    
    if not stores_owned_by_seller.exists():
        messages.info(request, "등록된 가게가 없습니다.")
        return render(request, 'reservations/seller_list.html', {'page_obj': []})

    qs = Reservation.objects.filter(store__in=stores_owned_by_seller).select_related('buyer__user').prefetch_related('items')

    status_filter = request.GET.get('status', '')
    if status_filter:
        qs = qs.filter(status=status_filter)

    qs = qs.order_by('-created_at')
    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_choices': ReservationStatus.choices,
        'status_now': status_filter,
        'reject_form': SellerReservationUpdateForm(),
    }
    return render(request, 'reservations/seller_list.html', context)


@login_required
@transaction.atomic
def reservation_create_from_form(request):
    """임시: 가게 상세 페이지의 폼으로부터 예약을 생성하는 뷰 (디버깅 코드 추가)"""
    if request.method != 'POST':
        return redirect('stores:store-list')

    buyer, jump = _require_buyer(request)
    if jump: return jump

    try:
        store_item_id = request.POST.get('item_id')
        store_id = request.POST.get('store_id')
        quantity = int(request.POST.get('quantity', 1))
        pickup_time_str = request.POST.get('pickup_time')

        store_item = get_object_or_404(StoreItem, pk=store_item_id)
        store = get_object_or_404(Store, pk=store_id)

        hh, mm = map(int, pickup_time_str.split(':'))
        today = timezone.localdate()
        requested_pickup_at = timezone.make_aware(datetime(today.year, today.month, today.day, hh, mm))

        if requested_pickup_at < timezone.now():
            messages.error(request, "과거 시간으로는 예약할 수 없습니다.")
            return redirect('stores:detail', store_id=store.id)

        reservation = Reservation.objects.create(
            store=store,
            buyer=buyer,
            requested_pickup_at=requested_pickup_at,
        )

        ReservationItem.objects.create(
            reservation=reservation,
            item_name=store_item.item.name,
            unit_price=store_item.price,
            quantity=quantity,
            unit=store_item.unit,
            original_item=store_item.item,
            image=store_item.photo,  # 여기서 이미지 복사!
        )

        messages.success(request, f"[Debug] '{buyer.user.username}'님이 '{store.name}' 가게에 예약을 생성했습니다 (Buyer ID: {buyer.id}, Store ID: {store.id})")
        return redirect('reservations:list')

    except Exception as e:
        messages.error(request, f"예약 중 오류가 발생했습니다: {e}")
        return redirect('stores:store-list')


# 구매 내역 상세 보기 리스트
@login_required
def purchase_list(request):
    buyer, jump = _require_buyer(request)
    if jump: return jump

    past_reservations = (
        Reservation.objects
        .filter(buyer=buyer, status=ReservationStatus.PICKED_UP)
        .select_related('store', 'store__seller')
        .prefetch_related('items')
        .order_by('-created_at')
    )

    return render(request, 'reservations/purchase_list.html', {
        'past_reservations': past_reservations,
    })

@require_POST
@login_required
def pickup_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id, buyer=request.user.buyer)
    if reservation.status != ReservationStatus.ACCEPTED:
        return JsonResponse({'status': 'error', 'message': '예약이 수락된 상태에서만 픽업 완료가 가능합니다.'})
    reservation.update_status(ReservationStatus.PICKED_UP)
    return JsonResponse({'status': 'success'})

@require_POST
@login_required
def pickup_ready_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id, buyer=request.user.buyer)
    if reservation.status != ReservationStatus.ACCEPTED:
        return JsonResponse({'status': 'error', 'message': '예약이 수락된 상태에서만 픽업 준비가 가능합니다.'})
    reservation.is_pickup_ready = True
    reservation.save()
    return JsonResponse({'status': 'success'})

@login_required
def reservation_item_create_view(request, item_id):
    """
    특정 StoreItem에 대한 예약 페이지를 보여주는 뷰 (GET 요청 처리)
    """
    buyer, jump = _require_buyer(request)
    if jump: return jump
    
    # URL로 받은 item_id로 예약할 상품(StoreItem) 객체를 찾습니다.
    item_to_reserve = get_object_or_404(StoreItem, pk=item_id)
    
    # 이 뷰는 폼을 보여주는 역할만 합니다.
    # 폼 제출(POST)은 다른 뷰(reservation_create_from_form)가 처리하도록 할 것입니다.
    context = {
        'item': item_to_reserve,
        'store': item_to_reserve.store
    }
    return render(request, 'reservations/reservation_create.html', context)