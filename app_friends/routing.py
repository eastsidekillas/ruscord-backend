from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/voice_call/', consumers.VoiceCallConsumer.as_asgi()),
]
