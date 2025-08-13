from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    path('', onboarding, name='onboarding'),
    path('auto-login/', auto_login, name='auto_login'),
    path('seller-step1/', seller_step1, name='seller_step1'),
    path('seller-step2/', seller_step2, name='seller_step2'),
    path('seller-step3/', seller_step3, name='seller_step3'),
    path('seller-step4/', seller_step4, name='seller_step4'),
    path('seller-step5/', seller_step5, name='seller_step5'),
    path('home/', home, name='home'),
    path('buyer-home/', buyer_home, name='buyer_home'),
    path('seller-home/', seller_home, name='seller_home'),
    path('signup/', signup, name='signup'), # 개발용
    path('login/', login, name='login'), # 개발용
    path('logout/', logout, name='logout'), # 개발용
]
