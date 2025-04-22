import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ruscord.settings')

application = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from app_auth.base_auth import JWTAuthMiddleware

import app_gateway.routing

application = ProtocolTypeRouter({
    "http": application,
    "websocket": JWTAuthMiddleware(
        URLRouter(
            app_gateway.routing.websocket_urlpatterns
        )
    ),
})
