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
        if user.usertype == 'SELLER':
            # 판매자 회원가입 후 온보딩 시작
            return redirect('users:seller_step1')
        else:
            # 구매자는 로그인 화면으로 이동
            return redirect('users:login')
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

@login_required
def seller_step2(request):
    if request.method == 'POST':
        registered = request.POST.get('store-registered')
        seller = request.user.seller
        seller.has_store = (registered == 'yes')
        seller.save()
        if registered == 'yes':
            return redirect('users:seller_step4')
        else:
            return redirect('users:seller_step5')
    return render(request, 'users/seller-step2.html')

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
        return render(request, 'users/buyer_home.html')
    elif role == 'SELLER':
        return render(request, 'users/seller_home.html')
    else:
        return redirect('users:onboarding')

@login_required
def buyer_home(request):
    return render(request, 'users/buyer_home.html')

@login_required
def seller_home(request):
    return render(request, 'users/seller_home.html')