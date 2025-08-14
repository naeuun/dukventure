import json
from django.http import JsonResponse
from django.db import transaction
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Reservation, ReservationItem, ReservationStatus
from .forms import ReservationForm, ReservationItemForm, SellerReservationUpdateForm
from users.models import UserType
from stores.models import Store
from items.models import Item   

# ... _require_buyer, _require_seller 등 헬퍼 함수 ...



@require_http_methods(["GET"])
def get_store_items_api(request, store_id):
    """API: 특정 가게의 판매 상품 목록을 JSON으로 반환 (필드명 수정)"""
    store = get_object_or_404(Store, pk=store_id)
    # Item 모델의 ForeignKey 필드 이름을 'stores'로 수정
    items = Item.objects.filter(stores=store)
    
    items_data = [{
        'id': item.id,
        'name': item.name,
        'price': item.price,
        'unit': item.unit,
        'photo_url': item.photo.url if item.photo else 'https://placehold.co/200x150?text=No+Image'
    } for item in items]
    
    return JsonResponse({'items': items_data})


@require_http_methods(["POST"])
@login_required
@transaction.atomic
def reservation_create_api(request):
    """API: JSON 데이터를 받아 예약을 생성"""
    buyer, jump = _require_buyer(request)
    if jump: return JsonResponse({'error': '권한이 없습니다.'}, status=403)

    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
        pickup_time_str = data.get('pickup_time')
        
        item = get_object_or_404(Item, pk=item_id)
        
        hh, mm = map(int, pickup_time_str.split(':'))
        today = timezone.localdate()
        requested_pickup_at = timezone.make_aware(datetime(today.year, today.month, today.day, hh, mm))

        if requested_pickup_at < timezone.now():
            return JsonResponse({'error': '과거 시간으로 예약할 수 없습니다.'}, status=400)

        reservation = Reservation.objects.create(
            store=item.store,
            buyer=buyer,
            requested_pickup_at=requested_pickup_at,
        )
        
        ReservationItem.objects.create(
            reservation=reservation,
            item_name=item.name,
            unit_price=item.price,
            quantity=quantity,
            unit=item.unit,
            original_item=item,
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
    if jump: return jump

    reservation_list = (Reservation.objects
        .filter(buyer=buyer)
        .select_related('store')
        .prefetch_related('items')
        .order_by('-created_at'))
    
    return render(request, 'reservations/reservation_list.html', {
        'reservations': reservation_list,
        'now': timezone.now(),
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
    """판매자/구매자: 예약 상태 변경 (AJAX 지원 강화, 리팩토링 버전)"""
    reservation = get_object_or_404(Reservation, pk=pk)
    to_status = request.POST.get('to_status')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    redirect_url = 'users:buyer_home' if request.user.usertype == UserType.BUYER else 'reservations:seller_list'

    if not reservation.can_transition_to(to_status, request.user):
        message = '허용되지 않는 요청이거나 권한이 없습니다.'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': message}, status=403)
        messages.error(request, message)
        return redirect(redirect_url)

    try:
        if to_status == ReservationStatus.REJECTED:
            form = SellerReservationUpdateForm(request.POST, instance=reservation)
            if form.is_valid():
                reservation.reject(
                    reason=form.cleaned_data.get('rejected_reason'),
                )
            else:
                raise ValueError('거절 사유를 올바르게 입력해주세요.')
        else:
            reservation.update_status(to_status)

        message = f'상태가 {reservation.get_status_display()}(으)로 변경되었습니다.'
        if is_ajax:
            return JsonResponse({
                'status': 'success',
                'message': message,
                'new_status': reservation.get_status_display()
            })
        
        messages.success(request, message)
        return redirect(redirect_url)

    except ValueError as e:
        message = str(e)
        if is_ajax:
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
        return redirect('stores:list')

    buyer, jump = _require_buyer(request)
    if jump: return jump

    try:
        item_id = request.POST.get('item_id')
        store_id = request.POST.get('store_id')
        quantity = int(request.POST.get('quantity', 1))
        pickup_time_str = request.POST.get('pickup_time')
        
        item = get_object_or_404(Item, pk=item_id)
        store = get_object_or_404(Store, pk=store_id)

        if not item.stores.filter(pk=store.id).exists():
            messages.error(request, "잘못된 접근입니다.")
            return redirect('stores:list')
        
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
            item_name=item.name,
            unit_price=item.price,
            quantity=quantity,
            unit=item.unit,
            original_item=item,
        )
        
        # [디버깅 메시지]
        messages.success(request, f"[Debug] '{buyer.user.username}'님이 '{store.name}' 가게에 예약을 생성했습니다 (Buyer ID: {buyer.id}, Store ID: {store.id})")
        return redirect('reservations:list')

    except Exception as e:
        messages.error(request, f"예약 중 오류가 발생했습니다: {e}")
        return redirect('stores:list')
