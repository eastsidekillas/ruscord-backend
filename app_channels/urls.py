from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DirectMessageChannelViewSet

router = DefaultRouter()
router.register(r'channels', DirectMessageChannelViewSet, basename='channel')

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns = router.urls


