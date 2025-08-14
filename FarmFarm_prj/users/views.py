from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.conf import settings
from users.models import User 
from users.forms import SignUpForm #개발용
from django.contrib.auth.forms import AuthenticationForm #개발용
from django.contrib.auth import login as auth_login  # 개발용 
from django.contrib.auth import logout as auth_logout # 개발용
from django.views.decorators.cache import never_cache # 뒤로가기 후 로그인했을 때 캐시 문제 해결
from django.http import JsonResponse 
from django.contrib.auth.decorators import login_required
from reservations.models import Reservation, ReservationStatus
from reviews.forms import ReviewForm 
from reviews.models import Review
from users.models import UserType
from django.contrib import messages 
from django.utils import timezone

@never_cache   
def onboarding(request):
    return render(request, 'users/onboarding.html')

#개발용 회원가입 
def signup(request):
    if request.method == 'GET':
        form = SignUpForm()
        return render(request, 'users/signup.html', {'form': form})
    form = SignUpForm(request.POST)
    
    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1']) # 안전하게 암호화해서 저장
        user.save()
        return redirect('users:login')  # 회원가입 후 로그인 페이지로 이동
    else:
        return render(request, 'users/signup.html', {'form': form})  # 유효성 검사 실패 시 다시 폼 보여주기
    
#개발용 로그인
def login(request):
    if request.method == 'GET':
        return render(request, 'users/login.html', {'form': AuthenticationForm()})
    form = AuthenticationForm(request, request.POST)
    if form.is_valid():
        auth_login(request, form.user_cache) 
        return redirect('users:onboarding')
    return render(request, 'users/login.html', {'form': form})

#개발용 로그아웃
def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('users:onboarding')  # 로그아웃 후 온보딩 페이지로 이동
    

def auto_login(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        if role == 'buyer':
            username = '김OO'
            password = settings.BUYER_PASSWORD  
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('users:buyer_home')  # 구매자 홈으로 이동

        elif role == 'seller':
            username = '박OO'
            password = settings.SELLER_PASSWORD
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('users:seller_home')  # 판매자 홈 화면으로 이동 

    return redirect('users:onboarding')  # GET 요청 또는 실패 시 홈으로 이동

def seller_step1(request):
    if request.method == 'POST':
        registered = request.POST.get('registered')
        # 필요하다면 Seller 모델에 저장
        # 예시: request.user.seller.is_registered = (registered == 'yes')
        # request.user.seller.save()
        if registered == 'yes':
            return redirect('users:seller_step2')  # 사업자 등록 O
        else:
            return redirect('users:seller_step3')  # 사업자 등록 X
    return render(request, 'users/seller-step1.html')

def seller_step2(request):
    if request.method == 'POST':
        registered = request.POST.get('store-registered')
        if registered == 'yes':
            return redirect('users:seller_step4')  # 가게 등록 O
        else:
            return redirect('users:seller_step5')  # 가게 등록 X

    return render(request, 'users/seller-step2.html')

def seller_step3(request):
    return render(request, 'users/seller-step3.html')

def seller_step4(request):
    return render(request, 'users/seller-step4.html')

def seller_step5(request):
    return render(request, 'users/seller-step5.html')

@login_required
def buyer_home(request):
    """구매자 홈: 예약 현황과 내가 쓴 리뷰를 함께 보여주는 뷰"""
    if request.user.usertype != UserType.BUYER or not hasattr(request.user, 'buyer'):
        return redirect('users:onboarding')

    buyer = request.user.buyer
    
    # 구매자와 관련된 모든 예약을 가져옵니다.
    all_reservations = Reservation.objects.filter(
        buyer=buyer
    ).select_related('store').prefetch_related('items').order_by('-created_at')

    # '진행 중'인 예약과 '지난' 예약을 구분합니다.
    active_statuses = [
        ReservationStatus.PENDING, 
        ReservationStatus.ACCEPTED, 
        ReservationStatus.PREPARING, 
        ReservationStatus.READY
    ]
    
    now = timezone.now()
    active_reservations = []
    for r in all_reservations:
        if r.status in active_statuses:
            # 템플릿에서 사용할 추가 정보를 객체에 직접 추가합니다.
            time_diff = r.requested_pickup_at - now
            r.remaining_minutes = time_diff.total_seconds() // 60
            active_reservations.append(r)

    past_reservations = [r for r in all_reservations if r.status not in active_statuses]

    # 내가 쓴 리뷰 목록
    my_reviews = Review.objects.filter(
        author=buyer
    ).select_related('store', 'author__user').order_by('-created_at')[:5]

    context = {
        'active_reservations': active_reservations,
        'past_reservations': past_reservations,
        'reviews': my_reviews,
        'review_form': ReviewForm(), # 리뷰 작성 모달을 위한 빈 폼
    }
    return render(request, 'users/buyer-home.html', context)



@login_required
def seller_home(request):
    # 판매자 권한 체크 (프로젝트에 맞게 보정)
    if request.user.usertype != UserType.SELLER or not hasattr(request.user, 'seller'):
        return redirect('users:onboarding')

    seller = request.user.seller
    store = getattr(seller, 'store', None)  # Seller에 store가 연결돼 있다고 가정

    reservations = Reservation.objects.none()
    if store:
        reservations = (Reservation.objects
                        .filter(store=store)
                        .select_related('buyer__user')
                        .prefetch_related('items'))

    return render(request, 'users/seller-home.html', {
        'reservations': reservations,
        'store': store,
    })