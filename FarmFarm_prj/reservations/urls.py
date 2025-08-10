# reservations/urls.py
from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    # JSON
    path('buyer/<int:buyer_id>.json', views.reservation_list_by_buyer, name='buyer_list_json'),
    path('store/<int:store_id>.json', views.reservation_list_by_store, name='store_list_json'),
    path('<int:pk>.json', views.reservation_detail, name='detail_json'),
    path('create/', views.reservation_create, name='create'),

    # 액션
    path('<int:pk>/accept/', views.reservation_accept, name='accept'),
    path('<int:pk>/reject/', views.reservation_reject, name='reject'),
    path('<int:pk>/ready/', views.reservation_ready, name='ready'),
    path('<int:pk>/picked-up/', views.reservation_picked_up, name='picked_up'),
    path('<int:pk>/cancel/', views.reservation_cancel, name='cancel'),
    path('<int:pk>/update-meta/', views.reservation_update_meta, name='update_meta'),

    # 페이지
    path('buyer/', views.page_buyer_reservations, name='buyer_page'),
    path('seller/', views.page_seller_reservations, name='seller_page'),
]
