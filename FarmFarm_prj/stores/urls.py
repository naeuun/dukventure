from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *

app_name = 'stores'

urlpatterns = [
    path('', map, name='map'),
    path('register/', register, name='register'),
    path('register-success/', register_success, name='register_success')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
