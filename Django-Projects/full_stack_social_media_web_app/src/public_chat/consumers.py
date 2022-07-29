from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json
from django.contrib.auth import get_user_model


MSG_TYPE_MESSAGE = 0 # for standard messages
User = get_user_model()



class PublicChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection
        """
        print("PublicChatConsumer: connect: " + str(self.scope['user']))
        await self.accept()

        # Add them to the group so that they get room messages
        await self.channel_layer.group_add(
            "General",
            self.channel_name
        )

    async def disconnect(self, code):
        """
        Called when the WebSocket closes for any reason
        """
        print("PublicChatConsumer: disconnect")
        
    
    async def receive_json(self, content):
        """
        Called when we get a text frame, Channels will JSON-decode the payload for us and pass it as the first argument.
        """
        command = content.get("command", None)
        message = content.get("message", None)
        print("PublicChatConsumer: receive_json: " + str(command))


        # print("PublicChatConsumer: message: " + str(message))
        try:
            if command == "send":
                if len(content['message'].lstrip()) == 0:
                    raise ClientError(422, "you can't send an empty message")

                await self.send_message(content['message'])
        except ClientError as e:
            errorData = {}
            errorData['error'] = e.code
            if e.message:
                errorData['message'] = e.message
            await self.send_json(errorData)

    async def send_message(self, message):
        await self.channel_layer.group_send(
            "General",
            {
                "type": "chat.message", # look for function chat_message and send the payload there
                "profile_image": self.scope['user'].profile_image.url,
                "username": self.scope['user'].username,
                "user_id": self.scope['user'].id,
                "message": message,
            }
        )



    async def chat_message(self, event):
        """
        Called when someone has messaged our chat

        """
        # Send a message down to the client
        print("PublicChatConsumer: chat_message from user #: " + str(event['user_id']))
        await self.send_json({
            "msg_type": MSG_TYPE_MESSAGE,
            "profile_image": event['profile_image'],
            "username": event['username'],
            "user_id": event['user_id'],
            "message": event['message'],
        })


class ClientError(Exception):
    """
    Custom exception class that is caught by the websocket receive()
    handler and translated into a send back to the client
    """
    def __init__(self, code, message):
        super().__init__(code)
        self.code = code
        if message:
            self.message = message

