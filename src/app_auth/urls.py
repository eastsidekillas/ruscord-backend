from django.urls import path
from .views import RegistrationAPIView, LoginAPIView, CheckAuthAPIView

urlpatterns = [

    path('auth/register/', RegistrationAPIView.as_view()),
    path('auth/login/', LoginAPIView.as_view()),
    path('auth/check/', CheckAuthAPIView.as_view(), name='check-auth'),

]

