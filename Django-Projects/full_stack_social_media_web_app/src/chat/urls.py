from django.urls import path

from .views import (
    private_chat_room_view,
)


app_name = "chat"

urlpatterns = [
    path("", private_chat_room_view, name="private-chat-room")
]