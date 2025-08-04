from django.urls import path
from .views import *

urlpatterns = [
    path("", commononboarding, name="commononboarding"),
    path("example", example, name="example"),
    path("selleronboarding1", selleronboarding1, name="selleronboarding1"),
    path("selleronboarding2", selleronboarding2, name="selleronboarding2"),
    path("selleronboarding3", selleronboarding3, name="selleronboarding3"),
    path("selleronboarding4", selleronboarding4, name="selleronboarding4"),
    path("selleronboarding5", selleronboarding5, name="selleronboarding5"),
    
    path("reservations", reservations, name="reservations"),
    path("storesplus", storesplus, name="storesplus"),
]
