from django.urls import path
from . import consumers

websocket_urlpatterns = [
    # Путь для голосового вызова
    path('ws/voice_call/', consumers.VoiceCallConsumer.as_asgi()),

    # Путь для личных сообщений
    path('ws/messages/', consumers.DirectMessageConsumer.as_asgi()),
]
