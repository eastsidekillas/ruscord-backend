from django.urls import re_path
from app_gateway.consumers.gateway import GatewayConsumer
from app_gateway.consumers.conversation import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/status/$', GatewayConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<channel_id>\w+)/$', ChatConsumer.as_asgi()),
]