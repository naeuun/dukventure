from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    path('', onboarding, name='onboarding'),
    path('role/<str:role>/', auto_login, name='auto_login'),
    path('home/', home, name='home'),
]
