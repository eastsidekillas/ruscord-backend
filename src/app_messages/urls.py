from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DirectMessageViewSet, ForwardTargetsView, ForwardMessageView

router = DefaultRouter()
UUID_RE = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
router.register(rf'channels/(?P<channel_id>{UUID_RE})/messages', DirectMessageViewSet, basename='direct-messages')

urlpatterns = router.urls + [
    path('messages/forward-targets/', ForwardTargetsView.as_view(), name='forward-targets'),
    path(f'messages/<uuid:message_id>/forward/', ForwardMessageView.as_view(), name='forward-message'),
]