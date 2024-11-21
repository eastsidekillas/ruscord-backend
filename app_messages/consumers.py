from uuid import UUID
import json
from django.core.exceptions import ValidationError
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


def get_channel_by_uuid(uuid):
    from app_channels.models import DirectMessageChannel
    try:
        return DirectMessageChannel.objects.get(uuid=uuid)
    except DirectMessageChannel.DoesNotExist:
        return None


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.uuid = self.scope['url_route']['kwargs']['uuid']
        self.room_group_name = f'dm_{self.uuid}'

        # Проверка существования канала
        self.channel = await database_sync_to_async(get_channel_by_uuid)(self.uuid)
        if not self.channel:
            await self.close()
            return

        # Присоединяемся к группе чата
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        from app_users.models import CustomUser
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_uuid = str(self.scope['user'].id)  # UUID текущего пользователя
        recipient_uuid = text_data_json['recipient']

        # Проверка корректности UUID
        try:
            sender = await database_sync_to_async(CustomUser.objects.get)(id=UUID(sender_uuid))
            recipient = await database_sync_to_async(CustomUser.objects.get)(id=UUID(recipient_uuid))
        except (ValueError, CustomUser.DoesNotExist):
            await self.send(text_data=json.dumps({'error': 'Invalid sender or recipient UUID'}))
            return

        from .models import Message
        # Сохранение сообщения в базе данных
        await database_sync_to_async(Message.objects.create)(
            sender=sender,
            recipient=recipient,
            text=message,
        )

        # Отправляем сообщение в группу
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.id,
                'sender_username': sender.username,
                'recipient': recipient.id,
            },
        )

    async def chat_message(self, event):
        # Отправляем сообщение клиенту
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'sender_username': event['sender_username'],
            'recipient': event['recipient'],
        }))
