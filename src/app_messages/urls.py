from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DirectMessageViewSet

router = DefaultRouter()
router.register(r'channels/(?P<channel_id>\d+)/messages', DirectMessageViewSet, basename='direct-messages')


urlpatterns = []

urlpatterns = router.urls

