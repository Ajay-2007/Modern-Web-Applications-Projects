from friend.models import FriendList
from chat.utils import find_or_create_private_chat

friend_lists = FriendList.objects.all()

for f in friend_lists:
    for friend in f.friends.all():
        chat = find_or_create_private_chat(f.user, friend)
        chat.is_active = True
        chat.save()