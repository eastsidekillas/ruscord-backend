import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from app_messages.models import Messages
from app_channels.models import Channel
from app_users.models import Profile
from ruscord.utils import build_absolute_uri

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.channel_id = self.scope['url_route']['kwargs']['channel_id']
        self.room_group_name = None
        self.profile = None

        if self.user.is_anonymous:
            await self.close()
            return

        try:
            self.channel = await database_sync_to_async(Channel.objects.get)(id=self.channel_id)
        except Channel.DoesNotExist:
            logger.warning("Channel %s not found", self.channel_id)
            await self.close()
            return

        self.profile = await database_sync_to_async(
            lambda: Profile.objects.filter(user=self.user).first()
        )()
        if not self.profile:
            await self.close()
            return

        is_participant = await database_sync_to_async(
            self.channel.participants.filter(id=self.profile.id).exists
        )()
        if not is_participant:
            logger.warning("User %s is not a participant of channel %s", self.user.id, self.channel_id)
            await self.close()
            return

        self.room_group_name = f"dm_{self.channel_id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if self.room_group_name:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        message_type = content.get('type')
        if message_type == 'typing':
            await self.handle_typing(content)
        elif message_type == 'chat.message':
            await self.handle_chat_message(content)
        elif message_type in ('call.request', 'call.response', 'call.ended'):
            await self.handle_call_event(content)
        else:
            logger.debug("Unknown message type: %s", message_type)

    async def handle_typing(self, event):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user.typing',
                'sender_username': self.profile.name,
                'sender_id': str(self.user.id),
                'typing': event.get('typing', False),
            }
        )

    async def user_typing(self, event):
        await self.send_json(event)

    async def handle_chat_message(self, event):
        message = event.get('message', '').strip()
        if not message:
            return

        reply_to_id = event.get('reply_to_id')
        reply_to_obj = None
        if reply_to_id:
            try:
                reply_to_obj = await database_sync_to_async(
                    Messages.objects.select_related('sender').get
                )(id=reply_to_id)
            except Messages.DoesNotExist:
                pass

        try:
            direct_message = await database_sync_to_async(Messages.objects.create)(
                channel=self.channel,
                sender=self.profile,
                content=message,
                reply_to=reply_to_obj,
            )
        except Exception as e:
            logger.error("Failed to save message for user %s: %s", self.user.id, e)
            return

        avatar_url = None
        if self.profile.avatar:
            headers = dict((k.decode(), v.decode()) for k, v in self.scope.get('headers', []))
            host = headers.get('host')
            scheme = self.scope.get('scheme', 'http')
            avatar_url = build_absolute_uri(self.profile.avatar.url, host, scheme)

        reply_preview = None
        if reply_to_obj:
            reply_preview = {
                'id': str(reply_to_obj.id),
                'content': reply_to_obj.content[:120],
                'sender_name': reply_to_obj.sender.name,
            }

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',
                'message': message,
                'sender_username': self.profile.name,
                'sender_avatar': avatar_url,
                'timestamp': direct_message.created_at.isoformat(),
                'sender_id': str(self.profile.id),
                'message_id': str(direct_message.id),
                'reply_to': reply_preview,
            }
        )

    async def chat_message(self, event):
        await self.send_json(event)

    async def handle_call_event(self, content):
        event_type = content.get('type')
        payload = {
            **content,
            'type': event_type,
            'sender_id': str(self.user.id),
            'sender_name': self.profile.name,
        }
        await self.channel_layer.group_send(self.room_group_name, payload)

    async def call_request(self, event):
        await self.send_json(event)

    async def call_response(self, event):
        await self.send_json(event)

    async def call_ended(self, event):
        await self.send_json(event)