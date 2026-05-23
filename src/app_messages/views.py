from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import viewsets, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.views import APIView
from rest_framework.response import Response

from app_auth.base_auth import CookieJWTAuthentication
from app_channels.models import Channel
from app_servers.models import Server
from ruscord.utils import build_absolute_uri
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

        return Messages.objects.filter(
            channel=channel, deleted=False
        ).select_related('sender', 'reply_to__sender', 'forwarded_from__sender').order_by('created_at')


class ForwardTargetsView(APIView):
    """Returns DM channels with friends + server text channels for the forward modal."""
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.profile

        # DM channels: scope=DM, user is participant, find the other person
        dm_channels = Channel.objects.filter(
            participants=profile, scope='DM', channel_type='TEXT'
        ).prefetch_related('participants').distinct()

        dms = []
        for ch in dm_channels:
            other = ch.participants.exclude(id=profile.id).first()
            if not other:
                continue
            avatar_url = None
            if other.avatar:
                avatar_url = request.build_absolute_uri(other.avatar.url)
            dms.append({
                'channel_id': str(ch.id),
                'friend_name': other.name,
                'friend_avatar': avatar_url,
            })

        # Servers: user is member, get text channels
        servers_qs = Server.objects.filter(members__profile=profile).prefetch_related('channels').distinct()

        servers = []
        for srv in servers_qs:
            text_channels = srv.channels.filter(channel_type='TEXT')
            if not text_channels.exists():
                continue

            srv_avatar = None
            if srv.avatar:
                srv_avatar = request.build_absolute_uri(srv.avatar.url)

            servers.append({
                'server_id': str(srv.id),
                'server_name': srv.name,
                'server_avatar': srv_avatar,
                'channels': [
                    {'id': str(ch.id), 'name': ch.name}
                    for ch in text_channels
                ],
            })

        return Response({'dms': dms, 'servers': servers})


class ForwardMessageView(APIView):
    """Forwards an existing message to a target channel."""
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, message_id):
        target_channel_id = request.data.get('target_channel_id')
        if not target_channel_id:
            return Response({'error': 'target_channel_id обязателен'}, status=400)

        # Validate original message
        try:
            original = Messages.objects.select_related('sender').get(
                id=message_id, deleted=False
            )
        except Messages.DoesNotExist:
            return Response({'error': 'Сообщение не найдено'}, status=404)

        # Validate target channel
        try:
            target_channel = Channel.objects.get(id=target_channel_id)
        except Channel.DoesNotExist:
            return Response({'error': 'Канал не найден'}, status=404)

        profile = request.user.profile
        if not target_channel.participants.filter(id=profile.id).exists():
            return Response({'error': 'Нет доступа к каналу'}, status=403)

        # Create forwarded message
        new_msg = Messages.objects.create(
            channel=target_channel,
            sender=profile,
            content=original.content,
            forwarded_from=original,
        )

        # Broadcast via WebSocket
        avatar_url = None
        if profile.avatar:
            avatar_url = request.build_absolute_uri(profile.avatar.url)

        channel_layer = get_channel_layer()
        room_group = f"dm_{target_channel_id}"

        async_to_sync(channel_layer.group_send)(
            room_group,
            {
                'type': 'chat.message',
                'message': new_msg.content,
                'sender_username': profile.name,
                'sender_avatar': avatar_url,
                'timestamp': new_msg.created_at.isoformat(),
                'sender_id': str(profile.id),
                'message_id': str(new_msg.id),
                'forwarded_from': {
                    'id': str(original.id),
                    'content': original.content[:120],
                    'sender_name': original.sender.name,
                },
            }
        )

        return Response({'message_id': str(new_msg.id)}, status=status.HTTP_201_CREATED)