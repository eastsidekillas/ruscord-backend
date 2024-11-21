from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DirectMessageChannelViewSet

router = DefaultRouter()
router.register(r'dm_channels', DirectMessageChannelViewSet, basename='dm_channel')

urlpatterns = [
    path('', include(router.urls)),
]

