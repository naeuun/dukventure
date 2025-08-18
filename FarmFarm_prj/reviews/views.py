from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from .models import Review
from .forms import ReviewForm
from reservations.models import Reservation, ReservationStatus
from users.models import UserType
from stores.models import Store
from django.views.decorators.http import require_POST

@login_required
def review_create(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # --- 권한 검증 ---
    if reservation.buyer.user != request.user:
        raise PermissionDenied("리뷰를 작성할 권한이 없습니다.")
    if reservation.status != ReservationStatus.PICKED_UP:
        message = "픽업이 완료된 예약에만 리뷰를 작성할 수 있습니다."
        if is_ajax: return JsonResponse({'status': 'error', 'message': message}, status=403)
        messages.error(request, message)
        return redirect('users:buyer_home')
    if hasattr(reservation, 'review'):
        message = "이미 리뷰를 작성한 예약입니다."
        if is_ajax: return JsonResponse({'status': 'error', 'message': message}, status=403)
        messages.error(request, message)
        return redirect('users:buyer_home')

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.reservation = reservation
            review.author = request.user.buyer
            review.store = reservation.store
            review.save()
            
            if is_ajax:
                return JsonResponse({'status': 'success', 'message': '소중한 리뷰가 등록되었습니다.'})
            
            messages.success(request, "소중한 리뷰가 등록되었습니다.")
            return redirect('users:buyer_home')
        else:
            message = "입력 내용을 확인해주세요."
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': message, 'errors': form.errors}, status=400)
            messages.error(request, message)
            # 폼이 유효하지 않을 때, 다시 폼을 렌더링하여 에러를 보여줄 수 있습니다.
            return render(request, 'reviews/review_form.html', {'form': form, 'reservation': reservation})
            
    else: # GET 요청 처리
        form = ReviewForm()
        # JavaScript가 fetch로 요청하면 이 폼 HTML을 응답으로 보냅니다.
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


@require_POST  # 데이터를 삭제하는 기능이므로 POST 요청만 허용합니다.
@login_required
def review_delete(request, review_id):
    """리뷰를 삭제하는 뷰 (AJAX 및 일반 요청 모두 지원)"""
    # 삭제할 리뷰 객체를 가져오거나, 없으면 404 에러를 발생시킵니다.
    review = get_object_or_404(Review, pk=review_id)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # --- 권한 검증 ---
    # 현재 로그인한 사용자가 해당 리뷰의 작성자인지 확인합니다.
    if review.author.user != request.user:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': '리뷰를 삭제할 권한이 없습니다.'}, status=403)
        # AJAX 요청이 아닐 경우, 권한 없음 페이지를 보여줍니다.
        raise PermissionDenied("이 리뷰를 삭제할 권한이 없습니다.")

    # 리뷰 삭제를 실행합니다.
    review.delete()

    # AJAX 요청에 대한 성공 응답
    if is_ajax:
        return JsonResponse({'status': 'success', 'message': '리뷰가 성공적으로 삭제되었습니다.'})

    # 일반적인 요청(비-AJAX)에 대한 성공 메시지 및 리디렉션
    messages.success(request, "리뷰가 성공적으로 삭제되었습니다.")
    return redirect('reviews:my_review_list') # 나의 리뷰 목록 페이지로 이동