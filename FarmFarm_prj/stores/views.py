from django.shortcuts import render

def map(request):
    return render(request, 'stores/map.html')

def register(request):
    return render(request, 'stores/register.html')
