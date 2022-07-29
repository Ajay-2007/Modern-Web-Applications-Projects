from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.contrib.auth import get_user_model
from django.contrib.humanize.templatetags.humanize import naturalday
from django.utils import timezone
from datetime import datetime

from public_chat.models import PublicChatRoom


MSG_TYPE_MESSAGE = 0 # for standard messages
User = get_user_model()



class PublicChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection
        """
        print("PublicChatConsumer: connect: " + str(self.scope['user']))


        await self.accept()

        self.room_id = None

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
        try:
            if self.room_id != None:
                await self.leave_room(self.room_id)
        except Exception:
            pass
        
    
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

                await self.send_room(content['room_id'], content['message'])
            elif command == "join":
                await self.join_room(content['room'])
            elif command == "leave":
                await self.leave_room(content['room'])
        except ClientError as e:
            await self.handle_client_error(e)

    async def send_room(self, room_id, message):
        """
        Called by receive_json when someone sends a message to a room
        """
        print("PublicChatConsumer: send_room")

        if self.room_id != None:
            if str(room_id) != str(self.room_id):
                raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")
            if not is_authenticated(self.scope['user']):
                raise ClientError("ROOM_ERROR", "You must be authenticated to chat.")
        else:
            raise ClientError("ROOM_ACCESS_DENIED", "Room access denied.")

        room = await get_room_or_error(room_id)

        await self.channel_layer.group_send(
            room.group_name,
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
        timestamp = calculate_timestamp(timezone.now())
        await self.send_json({
            "msg_type": MSG_TYPE_MESSAGE,
            "profile_image": event['profile_image'],
            "username": event['username'],
            "user_id": event['user_id'],
            "message": event['message'],
            "natural_timestamp": timestamp,
        })

    async def join_room(self, room_id):
        """
        Called by receive_json when someone sent a JOIN command
        """
        print("PublicChatConsumer: join_room")

        is_auth = is_authenticated(self.scope['user'])

        try:
            room = await get_room_or_error(room_id)
        except ClientError as e:
            await self.handle_client_error(e)
        
        # Add user to "users" list for room
        if is_auth:
            await connect_user(room, self.scope['user'])

        # Store that we're in the room
        self.room_id = room.id

        # Add them to the group so they get room messages
        await self.channel_layer.group_add(
            room.group_name,
            self.channel_name,
        )

        # Tell the client to finish opening the room
        await self.send_json({
            "join": str(room.id),
            "username": self.scope['user'].username,
        })

    async def leave_room(self, room_id):
        """
        Called by receive_json when someone sent a LEAVE command
        """
        print("PublicChatConsumer: leave_room")

        is_auth = is_authenticated(self.scope['user'])

        try:
            room = await get_room_or_error(room_id)
        except ClientError as e:
            await self.handle_client_error(e)

        # Remove user from "users" list
        if is_auth:
            await disconnect_user(room, self.scope['user'])
        # Remove that we're in the room
        self.room_id = None
        # Rmove them from the group so they no longer receive messages
        await self.channel_layer.group_discard(
            room.group_name,
            self.channel_name,
        )


    async def handle_client_error(self, e):
        """
        Called when a ClientError is raised.
        Sends error data to the UI
        """
        errorData = {}
        errorData['error'] = e.code
        if e.message:
            errorData['message'] = e.message
            await self.send_json(errorData)
        return


def is_authenticated(user):
    if user.is_authenticated:
        return True
    return False

@database_sync_to_async
def connect_user(room, user):
    return room.connect_user(user)

@database_sync_to_async
def disconnect_user(room, user):
    return room.disconnect_user(user)

@database_sync_to_async
def get_room_or_error(room_id):
    """
    Tries to fetch a room for the user
    """
    try:
        room = PublicChatRoom.objects.get(pk=room_id)
    except PublicChatRoom.DoesNotExist:
        raise ClientError("ROOM_INVALID", "Invalid room")
    return room



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


def calculate_timestamp(timestamp):

    """
    1. Today or yesterday:
        - EX: 'today at 10:56 AM'
        - EX: 'yesterday at 5:19 PM'
    2. other:
        - EX: 05/06/2020
        - EX: 12/28/2020
    """

    # today or yesterday
    if ((naturalday(timestamp) == "today") or (naturalday(timestamp) == "yesterday")):
        str_time = datetime.strftime(timestamp, "%I:%M %p")
        str_time = str_time.strip("0")
        ts = f"{naturalday(timestamp)} at {str_time}"
    else:
        str_time = datetime.strftime(timestamp, "%m/%d/%Y")
        ts = f"{str_time}"
    
    return ts