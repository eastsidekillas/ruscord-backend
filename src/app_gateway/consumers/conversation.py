from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from app_messages.models import Messages
from app_channels.models import Channel
from app_users.models import Profile
from ruscord.utils import build_absolute_uri
import json


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.channel_id = self.scope['url_route']['kwargs']['channel_id']
        self.room_group_name = None

        try:
            self.channel = await database_sync_to_async(Channel.objects.get)(id=self.channel_id)
        except Channel.DoesNotExist:
            print(f"Канал с ID {self.channel_id} не найден.")
            await self.close()
            return
        except Exception as e:
            print(f"Ошибка при получении канала: {e}")
            await self.close()
            return

        if self.user.is_anonymous:
            print(f"Анонимный пользователь пытается подключиться к каналу {self.channel_id}.")
            await self.close()
            return

        is_participant = await database_sync_to_async(self.channel.participants.filter(user=self.user).exists)()
        if not is_participant:
            print(f"Пользователь {self.user.id} не является участником канала {self.channel_id}.")
            await self.close()
            return

        self.room_group_name = f"dm_{self.channel_id}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"WebSocket соединение установлено для канала {self.channel_id} пользователем {self.user.id}.")

    async def disconnect(self, close_code):
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            print(
                f"WebSocket соединение разорвано для канала {self.channel_id} пользователем {self.user.id} с кодом {close_code}.")

    async def receive_json(self, content, **kwargs):
        message_type = content.get('type')
        if message_type == 'typing':
            await self.handle_typing(content)
        elif message_type == 'chat.message':
            await self.handle_chat_message(content)
        else:
            print(f"Неизвестный тип сообщения: {message_type}")

    async def handle_typing(self, event):
        user = self.scope['user']
        try:
            profile = await database_sync_to_async(Profile.objects.get)(user=user)
            username = profile.name if hasattr(profile, 'name') else user.username
        except Profile.DoesNotExist:
            print(f"Ошибка: Profile для пользователя {user.id} не найден.")
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user.typing',
                'sender_username': username,
                'sender_id': user.id,
                'typing': event.get('typing', False),
            }
        )

    async def user_typing(self, event):
        await self.send_json(event)

    async def handle_chat_message(self, event):
        message = event['message']
        sender_user = self.user
        try:
            profile = await database_sync_to_async(Profile.objects.get)(user=sender_user)
        except Profile.DoesNotExist:
            print(f"Ошибка: Profile для пользователя {sender_user.id} не найден.")
            return

        try:
            direct_message = await database_sync_to_async(Messages.objects.create)(
                channel=self.channel,
                sender=profile,
                content=message
            )
        except Exception as e:
            print(f"Ошибка при создании сообщения: {e}")
            return

        avatar_url = profile.avatar.url if profile.avatar else None
        if avatar_url and 'headers' in self.scope:
            headers = dict((k.decode(), v.decode()) for k, v in self.scope['headers'])
            host = headers.get('host')
            scheme = self.scope.get('scheme', 'http')
            avatar_url = build_absolute_uri(avatar_url, host, scheme)

        if self.room_group_name:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat.message',
                    'message': message,
                    'sender_username': profile.name if hasattr(profile, 'name') else sender_user.username,
                    'sender_avatar': avatar_url,
                    'timestamp': direct_message.created_at.isoformat(),
                    'sender_id': profile.id
                }
            )

    async def chat_message(self, event):
        await self.send_json(event)