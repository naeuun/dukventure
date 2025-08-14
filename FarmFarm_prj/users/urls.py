from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

app_name = 'users'

urlpatterns = [
    path('', onboarding, name='onboarding'),
    path('auto-login/', auto_login, name='auto_login'),
    path('seller-step1/', seller_step1, name='seller_step1'),
    path('seller-step2/', seller_step2, name='seller_step2'),
    path('seller-step3/', seller_step3, name='seller_step3'),
    path('home/', home, name='home'),
    path('buyer-home/', buyer_home, name='buyer_home'),
    path('seller-home/', seller_home, name='seller_home'),
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('seller-business-verify/', seller_business_verify, name='seller_business_verify'),
    path('profile-edit/', profile_edit, name='profile_edit'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
