from rest_framework import viewsets, permissions
from .models import Messages
from .serializers import DirectMessageSerializer
from app_auth.base_auth import CookieJWTAuthentication


class DirectMessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DirectMessageSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        channel_id = self.kwargs.get('channel_id')
        return Messages.objects.filter(channel_id=channel_id).order_by('created_at')
