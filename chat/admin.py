from django.contrib import admin
from chat.models import MyChats


@admin.register(MyChats)
class MyChatsAdmin(admin.ModelAdmin):

    list_display = ('id', 'me', 'frnd','chats')