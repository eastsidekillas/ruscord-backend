from django.urls import path
from .views import RegistrationAPIView, LoginAPIView, CheckAuthAPIView, TokenRefreshView, LogoutAPIView

urlpatterns = [
    path('auth/register/', RegistrationAPIView.as_view()),
    path('auth/login/', LoginAPIView.as_view()),
    path('auth/logout/', LogoutAPIView.as_view(), name='logout'),
    path('auth/check/', CheckAuthAPIView.as_view(), name='check-auth'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]

