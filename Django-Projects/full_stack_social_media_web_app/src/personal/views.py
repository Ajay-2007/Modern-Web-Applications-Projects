from django.shortcuts import render
from django.conf import settings

# Create your views here.
def home_screen_view(request, *args, **kwargs):
    context = {}
    context['debug_mode'] = settings.DEBUG
    context['room_id'] = 3

    return render(request, "personal/home.html", context)