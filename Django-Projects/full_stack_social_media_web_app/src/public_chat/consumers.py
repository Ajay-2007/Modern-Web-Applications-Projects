from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json
from django.contrib.auth import get_user_model

User = get_user_model()

class PublicChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection
        """
        print("PublicChatConsumer: connect: " + str(self.scope['user']))
        await self.accept()

    async def disconnect(self, code):
        """
        Called when the WebSocket closes for any reason
        """
        print("PublicChatConsumer: disconnect")
        
    
    async def receive_json(self, content):
        """
        Called when we get a text frame, Channels will JSON-decode the payload for us and pass it as the first argument.
        """
        command = content.get("comman", None)
        print("PublicChatConsumer: receive_json: " + str(command))