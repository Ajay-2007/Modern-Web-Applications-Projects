from django.contrib import admin
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db import models


from .models import PrivateChatRoom, RoomChatMessage

class PublicChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'user1', 'user2']
    search_fields = ['id', 'user1__username', 'user2__username', 'user1__email', 'user2__email']
    list_display = ['id']

    class Meta:
        model = PrivateChatRoom

admin.site.register(PrivateChatRoom, PublicChatRoomAdmin)

class CachingPaginator(Paginator):
    def _get_count(self):

        if not hasattr(self, "_count"):
            self._count = None
        
        if self._count is None:
            try:
                key = "adm:{0}:count".format(hash(self.object_list.query.__str__()))
                self._count = cache.get(key, -1)
                if self._count == -1:
                    self._count = super().count
                    cache.set(key, self._count, 3600)
            
            except:
                self._count = len(self.object_list)
        return self._count

    count = property(_get_count)


class RoomChatMessageAdmin(admin.ModelAdmin):
    list_filter = ['room', 'user', 'timestamp']
    list_display = ['room', 'user', 'content', 'timestamp']
    search_fields = ['user__username', 'content']
    readonly_fields = ['id', 'user', 'room', 'timestamp']

    show_full_result_count = False
    paginator = CachingPaginator

    class Meta:
        model = RoomChatMessage



admin.site.register(RoomChatMessage, RoomChatMessageAdmin)