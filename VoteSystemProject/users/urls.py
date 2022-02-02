from django.urls import path
from .views import UserRegisterView

urlpatterns = [
    path('registration/', UserRegisterView.as_view(), name="registration"),
    path('login/', UserRegisterView.as_view(), name="login"),
]
