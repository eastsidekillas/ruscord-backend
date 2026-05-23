from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DirectMessageViewSet

router = DefaultRouter()
UUID_RE = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
router.register(rf'channels/(?P<channel_id>{UUID_RE})/messages', DirectMessageViewSet, basename='direct-messages')


urlpatterns = router.urls

