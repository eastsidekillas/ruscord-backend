from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, csrf

router = DefaultRouter()
router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('csrf', csrf, name='csrf'),
]
