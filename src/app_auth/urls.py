from django.urls import path
from .views import RegistrationAPIView, LoginAPIView, CheckAuthAPIView, TokenRefreshView

urlpatterns = [

    path('auth/register/', RegistrationAPIView.as_view()),
    path('auth/login/', LoginAPIView.as_view()),
    path('auth/check/', CheckAuthAPIView.as_view(), name='check-auth'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='check-auth'),

]

