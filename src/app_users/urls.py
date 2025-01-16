from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserRegisterViewSet

# Создаем роутер и регистрируем UserViewSet
router = DefaultRouter()
router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Включаем маршруты для UserViewSet
    path('register/', UserRegisterViewSet.as_view(), name='user-register'),  # Путь для регистрации
]

