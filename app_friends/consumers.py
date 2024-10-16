import json
from channels.generic.websocket import AsyncWebsocketConsumer
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate

# Набор для хранения экземпляров RTCPeerConnection
pcs = set()

class VoiceCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        # Закрытие всех соединений при разрыве WebSocket
        for pc in pcs:
            await pc.close()
        pcs.clear()

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data['type'] == 'offer':
            pc = RTCPeerConnection()
            pcs.add(pc)

            @pc.on("icecandidate")
            async def on_icecandidate(candidate):
                if candidate:
                    await self.send(json.dumps({
                        'type': 'candidate',
                        'candidate': candidate.toJSON()
                    }))

            @pc.on("track")
            async def on_track(track):
                print("Received track: %s" % track.kind)

            offer = RTCSessionDescription(data['sdp'], data['type'])
            await pc.setRemoteDescription(offer)
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)

            await self.send(json.dumps({
                'type': 'answer',
                'sdp': pc.localDescription.sdp
            }))

        elif data['type'] == 'answer':
            pc = pcs.pop()
            answer = RTCSessionDescription(data['sdp'], data['type'])
            await pc.setRemoteDescription(answer)

        elif data['type'] == 'candidate':
            candidate = RTCIceCandidate(data['candidate'])
            pc = pcs.pop()
            await pc.addIceCandidate(candidate)


class DirectMessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.room_group_name = f'direct_messages_{self.user.id}'

        # Присоединяемся к группе
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Отсоединяемся от группы
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        # Отправляем сообщение в группу
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
