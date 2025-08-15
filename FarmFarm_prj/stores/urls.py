from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *


app_name = 'stores'

urlpatterns = [
    path('', map_view, name='map'),
    path('register/', register, name='register'),
    path('register-success/', register_success, name='register_success'),
    path('edit_store/<int:store_id>/', edit_store, name='edit_store'),
    path('edit_item/<int:item_id>/', edit_item, name='edit_item'),
    path('list/', store_list, name='store-list'), # 가게 목록 페이지
    path('<int:store_id>/', store_detail_view, name='detail'), # 가게 상세 페이지
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
