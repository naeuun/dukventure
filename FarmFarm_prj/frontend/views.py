from django.shortcuts import render

# Create your views here.
def example(request):
    return(render(request, "example.html"))

def selleronboarding1(request):
    return render(request, "seller_onboardings/seller_onboarding_1.html")
def selleronboarding2(request):
    return render(request, "seller_onboardings/seller_onboarding_2.html")
def signuppage(request):
    return render(request, "seller_onboardings/signup_page.html")
def selleronboarding3(request):
    return render(request, "seller_onboardings/seller_onboarding_3.html")
def selleronboarding4(request):
    return render(request, "seller_onboardings/seller_onboarding_4.html")
def selleronboarding5(request):
    return render(request, "seller_onboardings/seller_onboarding_5.html")
def selleronboarding6(request):
    return render(request, "seller_onboardings/seller_onboarding_6.html")
def commononboarding(request):
    return render(request, "common_onboarding.html")

def storesplus(request):
    return render(request, "stores_plus.html")

def storesseller(request):
    return render(request, "stores/stores_seller.html")

def storescustomer(request):
    return render(request, "stores/stores_customer.html")

def splash(request):
    return render(request, "splash.html")

def reservationsseller(request):
    return render(request, "reservations_seller.html")

def sellerhomepage(request):
    return render(request, "seller_homepage.html")
def sellerhomepage2(request): #연동 이후 홈페이지와 합칠 페이지입니다
    return render(request, "seller_homepage_ver2.html")

def shoppingpage(request):
    return render(request, "shopping_page.html")


def consumerprofile(request):
    return render(request, "consumer_home/consumer_profile.html")

def consumermain(request):
    return render(request, "consumer_home/consumer_main.html")

def characterhome(request):
    return render(request, "consumer_home/character_home.html")