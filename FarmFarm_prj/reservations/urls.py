from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('', views.reservation_list, name='list'),
    path('create/', views.reservation_create_form, name='create_form'),
    path('create/submit/', views.reservation_create, name='create'),
    path('<int:pk>/status/', views.reservation_change_status, name='change_status'),

    path('seller/', views.seller_reservation_list, name='seller_list'),
]
