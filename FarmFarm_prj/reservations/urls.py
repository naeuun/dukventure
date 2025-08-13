from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    # 구매자 URL
    path('my-list/', views.reservation_list, name='list'),
    path('create/', views.reservation_create_view, name='create'),

    # 판매자 URL
    path('seller-list/', views.seller_reservation_list, name='seller_list'),

    # 공통 URL (상태 변경)
    path('<int:pk>/change-status/', views.reservation_change_status, name='change_status'),
]
