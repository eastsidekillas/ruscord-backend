from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied, NotFound

from app_auth.base_auth import CookieJWTAuthentication
from app_channels.models import Channel
from .models import Messages
from .serializers import DirectMessageSerializer


class MessagePagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class DirectMessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DirectMessageSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MessagePagination

    def get_queryset(self):
        channel_id = self.kwargs.get('channel_id')

        try:
            channel = Channel.objects.get(id=channel_id)
        except Channel.DoesNotExist:
            raise NotFound('Канал не найден')

        if not channel.participants.filter(user=self.request.user).exists():
            raise PermissionDenied('Вы не являетесь участником этого канала')

        return Messages.objects.filter(channel=channel, deleted=False).order_by('created_at')
