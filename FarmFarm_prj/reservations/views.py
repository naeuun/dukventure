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
    """판매자/구매자: 예약 상태 변경"""
    r = get_object_or_404(Reservation, pk=pk)
    to_status = request.POST.get('to_status')

    # 모델 메서드를 통해 권한 검사 및 상태 전이 가능 여부 확인
    if not r.can_transition_to(to_status, request.user):
        messages.error(request, '허용되지 않는 요청이거나 권한이 없습니다.')
        # 사용자에 따라 적절한 리다이렉트 경로 설정
        redirect_url = 'reservations:list' if request.user.usertype == UserType.BUYER else 'reservations:seller_list'
        return redirect(redirect_url)

    # 상태 변경 로직 실행
    if to_status == ReservationStatus.REJECTED:
        # 거절의 경우, form을 통해 거절 사유를 받음
        form = SellerReservationUpdateForm(request.POST, instance=r)
        if form.is_valid():
            # 모델 메서드를 통해 거절 처리
            r.reject(
                reason=form.cleaned_data.get('rejected_reason'),
                detail=form.cleaned_data.get('rejected_reason_detail')
            )
            messages.success(request, '예약을 거절했습니다.')
        else:
            messages.error(request, '거절 사유를 올바르게 입력해주세요.')
    else:
        # 그 외 상태 변경은 모델 메서드를 통해 처리
        r.update_status(to_status)
        messages.success(request, f'예약 상태가 {r.get_status_display()}(으)로 변경되었습니다.')
    
    redirect_url = 'reservations:list' if request.user.usertype == UserType.BUYER else 'reservations:seller_list'
    return redirect(redirect_url)


@login_required
def seller_reservation_list(request):
    """판매자: 내 가게 예약 목록 (필터링, 페이지네이션 포함)"""
    seller, jump = _require_seller(request)
    if jump: return jump

    # 판매자가 여러 가게를 가질 수 있으므로 filter 사용
    # seller 모델에 'stores' related_name이 있다고 가정
    stores = seller.stores.all()
    if not stores.exists():
        messages.info(request, '아직 등록된 가게가 없습니다. 가게를 먼저 등록해주세요.')
        return render(request, 'reservations/seller_list.html', {'page_obj': []})

    qs = Reservation.objects.filter(store__in=stores)

    # 필터링
    status = request.GET.get('status', '')
    date = request.GET.get('date', '')
    q = request.GET.get('q', '').strip()

    if status:
        qs = qs.filter(status=status)
    if date:
        qs = qs.filter(created_at__date=date)
    if q:
        qs = qs.filter(Q(buyer__user__username__icontains=q) | Q(reservation_code__iexact=q))

    # 페이지네이션
    paginator = Paginator(qs.order_by('-created_at'), 10) # 한 페이지에 10개씩
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 거절 모달을 위한 빈 폼
    seller_update_form = SellerReservationUpdateForm()

    return render(request, 'reservations/seller_list.html', {
        'stores': stores,
        'page_obj': page_obj,
        'status_now': status,
        'q': q,
        'date': date,
        'status_choices': ReservationStatus.choices,
        'seller_update_form': seller_update_form, # 모달 폼 전달
    })