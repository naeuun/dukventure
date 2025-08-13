from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # 리뷰 생성 (예약 ID 필요)
    path('create/<int:reservation_id>/', views.review_create, name='create'),
    
    # 구매자: 내가 쓴 리뷰 목록
    path('my-reviews/', views.my_review_list, name='my_list'),
    
    # 판매자: 내 가게에 달린 리뷰 목록
    path('store-reviews/', views.store_review_list, name='store_list'),
]
