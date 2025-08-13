from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from .models import Review
from .forms import ReviewForm
from reservations.models import Reservation, ReservationStatus
from users.models import UserType, Seller
from stores.models import Store

@login_required
def review_create(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)

    # --- 권한 검증 ---
    # 1. 본인의 예약이 맞는지 확인
    if reservation.buyer.user != request.user:
        raise PermissionDenied("리뷰를 작성할 권한이 없습니다.")
    # 2. '픽업 완료' 상태인지 확인
    if reservation.status != ReservationStatus.PICKED_UP:
        messages.error(request, "픽업이 완료된 예약에만 리뷰를 작성할 수 있습니다.")
        return redirect('reservations:list')
    # 3. 이미 리뷰를 작성했는지 확인
    if hasattr(reservation, 'review'):
        messages.error(request, "이미 리뷰를 작성한 예약입니다.")
        return redirect('reservations:list')

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.reservation = reservation
            review.author = request.user.buyer
            review.store = reservation.store
            review.save()
            messages.success(request, "소중한 리뷰가 등록되었습니다.")
            return redirect('reservations:list')
    else:
        form = ReviewForm()

    return render(request, 'reviews/review_form.html', {
        'form': form,
        'reservation': reservation,
    })

@login_required
def my_review_list(request):
    """구매자가 본인이 작성한 리뷰 목록을 보는 페이지"""
    if request.user.usertype != UserType.BUYER:
        raise PermissionDenied("구매자만 접근할 수 있습니다.")
    
    reviews = Review.objects.filter(author=request.user.buyer).select_related('store', 'author__user')
    return render(request, 'reviews/my_review_list.html', {'reviews': reviews})

@login_required
def store_review_list(request):
    """판매자가 자신의 가게에 달린 리뷰 목록을 보는 페이지 (개선된 버전)"""
    if request.user.usertype != UserType.SELLER:
        raise PermissionDenied("판매자만 접근할 수 있습니다.")

    # 현재 로그인한 판매자 객체를 가져옵니다.
    seller = getattr(request.user, 'seller', None)
    if not seller:
        raise PermissionDenied("판매자 프로필이 존재하지 않습니다.")

    # 판매자가 소유한 모든 가게를 가져옵니다.
    # (Store 모델에 seller라는 이름의 ForeignKey가 있다고 가정)
    stores_owned_by_seller = Store.objects.filter(seller=seller)

    if not stores_owned_by_seller.exists():
        messages.info(request, "등록된 가게가 없습니다.")
        return render(request, 'reviews/store_review_list.html', {'reviews': []})

    # 판매자의 모든 가게에 달린 리뷰들을 한 번에 가져옵니다.
    reviews = Review.objects.filter(store__in=stores_owned_by_seller).select_related('author__user')
    
    return render(request, 'reviews/store_review_list.html', {'reviews': reviews})