from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.conf import settings
from users.models import User 
from users.forms import SignUpForm #개발용
from django.contrib.auth.forms import AuthenticationForm #개발용
from django.contrib.auth import login as auth_login  # 개발용 
from django.contrib.auth import logout as auth_logout # 개발용
from django.views.decorators.cache import never_cache # 뒤로가기 후 로그인했을 때 캐시 문제 해결
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import requests
import json

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
        user.set_password(form.cleaned_data['password1'])
        user.save()
        auth_login(request, user)
        if user.usertype == 'SELLER':
            return redirect('users:seller_step1')
        else:
            return redirect('users:buyer_home')
    return render(request, 'users/signup.html', {'form': form})


def login(request):
    if request.method == 'GET':
        return render(request, 'users/login.html', {'form': AuthenticationForm()})
    form = AuthenticationForm(request, request.POST)
    if form.is_valid():
        auth_login(request, form.user_cache)
        return redirect('users:onboarding')
    return render(request, 'users/login.html', {'form': form})

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
            return redirect('users:home')
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

    # 국세청 사업자등록 상태조회 API
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
    if request.method == 'POST':
        business_number = request.POST.get('business_number')
        is_valid = check_business_number(business_number)

        seller = request.user.seller
        seller.business_number = business_number
        seller.is_registered = is_valid
        seller.save()

        if is_valid:
            return redirect('users:seller_step4')  # 인증 성공 시 다음 단계
        else:
            return render(request, 'users/seller-step2.html', {'error': '유효하지 않은 사업자등록번호입니다.'})

    return render(request, 'users/seller-step2.html')


def seller_business_verify(request):
    if request.method == 'POST':
        business_number = request.POST.get('business_number')
        is_valid = check_business_number(business_number)
        return JsonResponse({'is_valid': is_valid})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def seller_step3(request):
    return render(request, 'users/seller-step3.html')

@login_required
def seller_step4(request):
    return render(request, 'users/seller-step4.html')

@login_required
def seller_step5(request):
    return render(request, 'users/seller-step5.html')

@login_required
def home(request):
    role = request.user.usertype
    if role == 'BUYER':
        return render(request, 'users/buyer-home.html')
    elif role == 'SELLER':
        return render(request, 'users/seller-home.html')
    else:
        return redirect('users:onboarding')

@login_required
def buyer_home(request):
    return render(request, 'users/buyer-home.html')

@login_required
def seller_home(request):
    return render(request, 'users/seller-home.html')


