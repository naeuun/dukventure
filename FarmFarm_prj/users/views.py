from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.conf import settings
from users.models import User 
from django.views.decorators.cache import never_cache # 뒤로가기 후 로그인했을 때 캐시 문제 해결

@never_cache   
def onboarding(request):
    return render(request, 'users/onboarding.html')

def auto_login(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        if role == 'buyer':
            username = 'buyer'
            password = settings.BUYER_PASSWORD  
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('users:buyer_home')  # 구매자 홈으로 이동

        elif role == 'seller':
            username = 'seller'
            password = settings.SELLER_PASSWORD
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
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