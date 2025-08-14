from django.urls import path
from .views import *

urlpatterns = [
    path("", splash, name="splash"),

    path("commononboarding", commononboarding, name="commononboarding"),
    path("example", example, name="example"),
    path("selleronboarding1", selleronboarding1, name="selleronboarding1"),
    path("signuppage", signuppage, name="signuppage"),
    path("selleronboarding2", selleronboarding2, name="selleronboarding2"),
    path("selleronboarding3", selleronboarding3, name="selleronboarding3"),
    path("selleronboarding4", selleronboarding4, name="selleronboarding4"),
    path("selleronboarding5", selleronboarding5, name="selleronboarding5"),
    path("selleronboarding6", selleronboarding6, name="selleronboarding6"),
    
    path("storesplus", storesplus, name="storesplus"),
    
    path("storesseller", storesseller, name="storesseller"),
    path("storescustomer", storescustomer, name="storescustomer"),
    
    path("reservationsseller", reservationsseller, name="reservationsseller"),
    
    path("sellerhomepage", sellerhomepage, name="sellerhomepage"),
    path("sellerhomepage2", sellerhomepage2, name="sellerhomepage2"),
    
    path("shoppingpage", shoppingpage, name="shoppingpage"),

    path("consumerprofile", consumerprofile, name="consumerprofile"),
]
