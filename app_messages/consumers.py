import json
from channels.generic.websocket import AsyncWebsocketConsumer


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

        # Отправляем сообщение в группу чата
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # Отправляем сообщение пользователю
        await self.send(text_data=json.dumps({
            'message': message
        }))
