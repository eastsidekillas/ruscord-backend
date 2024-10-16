from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DirectMessageViewSet, FriendshipViewSet

router = DefaultRouter()
router.register(r'friendships', FriendshipViewSet, basename='friendship')
router.register(r'messages', DirectMessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
]
