from django.shortcuts import render

# Create your views here.
def example(request):
    return(render(request, "example.html"))

def selleronboarding1(request):
    return render(request, "seller_onboardings/seller_onboarding_1.html")
def selleronboarding2(request):
    return render(request, "seller_onboardings/seller_onboarding_2.html")
def selleronboarding3(request):
    return render(request, "seller_onboardings/seller_onboarding_3.html")
def selleronboarding4(request):
    return render(request, "seller_onboardings/seller_onboarding_4.html")
def selleronboarding5(request):
    return render(request, "seller_onboardings/seller_onboarding_5.html")
def commononboarding(request):
    return render(request, "common_onboarding.html")