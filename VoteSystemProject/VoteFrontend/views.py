from django.shortcuts import render
# Create your views here.


def home(request):
    return render(request, "partial/home.html")


# def login(request):
#     return render(request, "partial/login.html")
#
#
# def register(request):
#     return render(request, "partial/register.html")
