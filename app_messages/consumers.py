import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.recipient_id = self.scope['url_route']['kwargs']['recipient_id']
        self.room_group_name = f'chat_{self.recipient_id}'

        # Присоединяемся к группе чата
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = self.scope['user'].id
        if sender is None:
            print("Sender is not authenticated!")
        else:
            print(f"Sender ID: {sender}")
        sender_username = self.scope['user'].username if self.scope['user'].is_authenticated else ''
        recipient = self.recipient_id  # Получаем ID получателя из URL

        # Отправляем сообщение в группу чата с данными отправителя и получателя
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender,  # Отправитель
                'sender_username': sender_username,
                'recipient': recipient,  # Получатель
            }
        )

    async def chat_message(self, event):
        # Получаем сообщение и данные об отправителе и получателе из события
        message = event['message']
        sender = event['sender']
        sender_username = event['sender_username']
        recipient = event['recipient']

        # Отправляем данные на фронтенд
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'sender_username': sender_username,
            'recipient': recipient,
        }))
