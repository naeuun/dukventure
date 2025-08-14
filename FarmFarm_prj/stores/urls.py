from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *
from . import views

app_name = 'stores'

urlpatterns = [
    #path('',map_view, name='map'),
    path('', views.store_list_view, name='list'), # 가게 목록 페이지
    path('<int:store_id>/', views.store_detail_view, name='detail'), # 가게 상세 페이지
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
