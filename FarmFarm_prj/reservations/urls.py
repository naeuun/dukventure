from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    # API: 특정 가게의 상품 목록을 JSON으로 반환
    path('api/store/<int:store_id>/items/', views.get_store_items_api, name='api_get_store_items'),

    # API: 예약 생성
    path('api/create/', views.reservation_create_api, name='api_create'),
    path('create/item/<int:item_id>/', views.reservation_item_create_view, name='create_for_item'),
    # 페이지: 구매자/판매자 예약 목록
    path('my-list/', views.reservation_list, name='list'),
    path('seller-list/', views.seller_reservation_list, name='seller_list'),
    
    # 상태 변경
    path('<int:pk>/change-status/', views.reservation_change_status, name='change_status'),

    # 임시 예약 생성을 위한 URL
    path('create-from-form/', views.reservation_create_from_form, name='create_from_form'),
    
    # 구매 내역 전체 보기 리스트
    path('purchase-list/', views.purchase_list, name='purchase-list'),
    
    # 픽업 처리
    path('<int:reservation_id>/pickup/', views.pickup_reservation, name='pickup_reservation'),
]

