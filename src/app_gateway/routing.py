from django.urls import re_path
from app_gateway.consumers.gateway import GatewayConsumer
from app_gateway.consumers.conversation import ChatConsumer

UUID_RE = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

websocket_urlpatterns = [
    re_path(r'ws/status/$', GatewayConsumer.as_asgi()),
    re_path(rf'ws/chat/(?P<channel_id>{UUID_RE})/$', ChatConsumer.as_asgi()),
]