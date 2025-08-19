from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from users.forms import SignUpForm, ProfileEditForm
from django.contrib.auth.forms import AuthenticationForm 
from django.views.decorators.cache import never_cache # 뒤로가기 후 로그인했을 때 캐시 문제 해결
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from reservations.models import Reservation, ReservationStatus
from reviews.forms import ReviewForm 
from reviews.models import Review
from users.models import UserType
from django.contrib import messages 
from django.utils import timezone
import requests
import json

@never_cache
def onboarding(request):
    if request.user.is_authenticated:
        if request.user.usertype == 'BUYER':
            return redirect('users:buyer_home')
        elif request.user.usertype == 'SELLER':
            return redirect('users:seller_home')
    return render(request, 'users/onboarding.html')

@never_cache
def signup_type(request):
    if request.method == "POST":
        usertype = request.POST.get("usertype")
        request.session["usertype"] = usertype  # 세션에 저장
        return redirect("users:signup")  # 다음 단계로 이동
    return render(request, "users/signup_type.html")
    
def signup(request):
    usertype = request.session.get("usertype")  # 세션에서 가져오기
    if not usertype:
        return redirect("users:signup_type")  # 유형 선택 안 했으면 타입 선택으로 이동

    if request.method == 'GET':
        form = SignUpForm()
        return render(request, 'users/signup.html', {'form': form})
    
    form = SignUpForm(request.POST)
        
    if form.is_valid():
        user = form.save(commit=False)
        # 세션에서 가져온 usertype 적용
        user.usertype = usertype
        user.save()  # commit=True로 DB 저장
        auth_login(request, user)
        
        # ✅ 비밀번호 인증 후 로그인
        user = authenticate(
            request,
            username=user.username,
            password=form.cleaned_data['password1']
        )
        if user is not None:
            auth_login(request, user)

            if user.usertype == 'SELLER':
                return redirect('users:seller_step1')
            else:
                return redirect('users:buyer_home')
        else:
            print("❌ 로그인 실패: authenticate가 None 반환")
    else:
        print(form.errors)
    return render(request, 'users/signup.html', {'form': form})


def login(request):
    error_message = None
    if request.method == 'GET':
        return render(request, 'users/login.html', {'form': AuthenticationForm()})
    form = AuthenticationForm(request, request.POST)
    
    if form.is_valid():
        auth_login(request, form.user_cache)
        usertype = form.user_cache.usertype
        if usertype == 'SELLER':
            return redirect('users:seller_home')
        elif usertype == 'BUYER':
            return redirect('users:buyer_home')
        else:
            return redirect('users:onboarding')
    else:
        error_message = "아이디 또는 비밀번호가 잘못 되었습니다.\n아이디와 비밀번호를 정확히 입력해 주세요."
    return render(request, 'users/login.html', {'form': form, 'error_message': error_message})

def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('users:onboarding')

def auto_login(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        if role == 'buyer':
            username = '김OO'
            password = settings.BUYER_PASSWORD
        elif role == 'seller':
            username = '박OO'
            password = settings.SELLER_PASSWORD
        else:
            return redirect('users:onboarding')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            role = request.user.usertype
            if role == 'BUYER':
                return redirect('users:buyer_home')
            elif role == 'SELLER':
                return redirect('users:seller_home')
            else:
                return redirect('users:onboarding')
    return redirect('users:onboarding')

@login_required
def seller_step1(request):
    if request.method == 'POST':
        registered = request.POST.get('registered')
        seller = request.user.seller
        seller.is_registered = (registered == 'yes')
        seller.save()
        if registered == 'yes':
            return redirect('users:seller_step2')
        else:
            return redirect('users:seller_step3')
    return render(request, 'users/seller-step1.html')

# 테스트 모드: API 호출 없이 True 반환할 사업자번호 (개발용)
TEST_VALID_BUSINESS_NUMBERS = [
    "1234567890",  # 테스트용 정상 번호
    "1111111111"
]

def check_business_number(business_number):
    # 하이픈 제거
    business_number = business_number.replace("-", "")

    # 테스트 모드 처리
    if business_number in TEST_VALID_BUSINESS_NUMBERS:
        return True

    # 공공 데이터 포털 - 국세청 사업자 등록 (상태 조회)
    service_key = "0YKRXsmW1KINyKdg6Xk%2BAKRSZ3j26xCEka8xG5lGtDjCOEuwUeppamSFWgL6xf6Ov8Y8%2B51zdDG83Tjpdv5lUQ%3D%3D"
    url = f"https://api.odcloud.kr/api/nts-businessman/v1/status?serviceKey=0YKRXsmW1KINyKdg6Xk%2BAKRSZ3j26xCEka8xG5lGtDjCOEuwUeppamSFWgL6xf6Ov8Y8%2B51zdDG83Tjpdv5lUQ%3D%3D"

    payload = {
        "b_no": [business_number]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            data = response.json()

            if data.get("data") and len(data["data"]) > 0:
                b_stt_cd = data["data"][0].get("b_stt_cd")  # 사업자 상태 코드
                # 01 → 계속사업자(영업 중)
                return b_stt_cd == "01"

        return False
    except Exception as e:
        print("API 호출 오류:", e)
        return False


@login_required
def seller_step2(request):
    return render(request, 'users/seller-step2.html')


@login_required
def seller_business_verify(request):
    if request.method == 'POST':
        business_number = request.POST.get('business_number')
        is_valid = check_business_number(business_number)
        seller = request.user.seller
        seller.business_number = business_number
        seller.is_registered = is_valid
        seller.save()
        return JsonResponse({'is_valid': is_valid})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def seller_step3(request):
    return render(request, 'users/seller-step3.html')



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


    # 내가 쓴 리뷰 목록
    my_reviews = Review.objects.filter(
        author=buyer
    ).select_related('store', 'author__user').order_by('-created_at')[:5]

    # 픽업 완료된 예약 내역만 추출 = 구매 내역 
    past_reservations = Reservation.objects.filter(
        buyer=request.user.buyer,
        status='PICKED_UP'
    ).order_by('-created_at')

    context = {
        'active_reservations': active_reservations,
        'past_reservations': past_reservations,
        'reviews': my_reviews,
        'review_form': ReviewForm(), # 리뷰 작성 모달을 위한 빈 폼
    }
    return render(request, 'users/buyer-home.html', context)

@login_required
def seller_home(request):
    # 판매자 권한 체크
    if request.user.usertype != UserType.SELLER or not hasattr(request.user, 'seller'):
        return redirect('users:onboarding')
    seller = request.user.seller
    store = getattr(seller, 'store', None)
    reviews = Review.objects.none() 

    reservations = Reservation.objects.none()
    if store:
        reservations = (Reservation.objects
                        .filter(store=store)
                        .select_related('buyer__user')
                        .prefetch_related('items'))
        reviews = store.reviews.all()  

    return render(request, 'users/seller-home.html', {
        'reservations': reservations,
        'store': store,
        'reviews': reviews,
    })

@login_required
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        edit_type = request.POST.get('edit_type')
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            # 사진만 수정
            if edit_type == 'image':
                user.profile_image = form.cleaned_data['profile_image']
                user.save()
            # 이름만 수정
            elif edit_type == 'name':
                user.username = form.cleaned_data['username']
                user.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = ProfileEditForm(instance=user)
        return render(request, 'users/profile_edit_form.html', {'form': form})