from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
# from django.core.asgi import get_asgi_application

from public_chat.consumers import PublicChatConsumer
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ChatServerPlayground.settings")

# django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    # 'http': django_asgi_app,
    'websocket' : AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path("public_chat/<room_id>/", PublicChatConsumer)
            ])
        )
    ),
})