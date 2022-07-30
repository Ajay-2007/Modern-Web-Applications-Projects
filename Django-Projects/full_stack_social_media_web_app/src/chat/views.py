from django.shortcuts import render, redirect
from django.conf import settings

from .models import PrivateChatRoom, RoomChatMessage

DEBUG = False

def private_chat_room_view(request, *args, **kwargs):

    user = request.user

    if not user.is_authenticated:
        return redirect("login")

    context = {}
    context['debug'] = DEBUG
    context['debug_mode'] = settings.DEBUG

    return render(request, "chat/snippets/room.html", context)