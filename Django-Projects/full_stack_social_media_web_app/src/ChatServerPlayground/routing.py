from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
# from django.core.asgi import get_asgi_application

from public_chat.consumers import PublicChatConsumer
from chat.consumers import ChatConsumer
import os

from notification.consumers import NotificationConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ChatServerPlayground.settings")

# django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    # 'http': django_asgi_app,
    'websocket' : AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path('', NotificationConsumer),
                path('chat/<room_id>/', ChatConsumer),
                path("public_chat/<room_id>/", PublicChatConsumer),
            ])
        )
    ),
})