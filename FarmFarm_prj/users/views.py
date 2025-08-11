from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.conf import settings
from users.models import User 
from users.forms import SignUpForm #개발용
from django.contrib.auth.forms import AuthenticationForm #개발용
from django.contrib.auth import login as auth_login  # 개발용 
from django.contrib.auth import logout as auth_logout # 개발용
from django.views.decorators.cache import never_cache # 뒤로가기 후 로그인했을 때 캐시 문제 해결

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
                return redirect('users:seller_step1')  # 구매자 온보딩 화면으로 이동 

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

def buyer_home(request):
    return render(request, 'users/buyer-home.html')

def seller_home(request):
    return render(request, 'users/seller-home.html')