import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_name = f"chat_{self.user_id}"

        # Проверка, что пользователь аутентифицирован
        if self.scope['user'].is_authenticated:
            # Подключение к комнате
            await self.channel_layer.group_add(
                self.room_name,
                self.channel_name
            )
            await self.accept()
        else:
            # Отклонить подключение, если пользователь не аутентифицирован
            await self.close()

    async def disconnect(self, close_code):
        # Отключение от комнаты
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        CustomUser = get_user_model()
        from .models import DirectMessage

        # Проверка, что пользователь аутентифицирован
        if not self.scope['user'].is_authenticated:
            await self.close()
            return

        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Получаем отправителя и получателя
        sender = self.scope['user']
        receiver_id = self.user_id

        try:
            receiver = CustomUser.objects.get(id=receiver_id)
        except CustomUser.DoesNotExist:
            await self.close()
            return

        # Сохранение сообщения в базе данных
        direct_message = DirectMessage.objects.create(
            sender=sender,
            receiver=receiver,
            content=message
        )

        # Отправка сообщения в комнату
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.id  # Отправляем ID отправителя
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Отправляем сообщение клиенту
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
        }))
