from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.conf import settings
from users.models import User 

def auto_login(request, role):
    if role == 'buyer':
        username = 'buyer'
        password = settings.BUYER_PASSWORD  
        
    elif role == 'seller':
        username = 'seller'
        password = settings.SELLER_PASSWORD

    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        return redirect('users:home')  # 로그인 후 이동할 페이지로 수정

    
def onboarding(request):
    return render(request, 'users/onboarding.html')

def home(request):
    return render(request, 'users/home.html')