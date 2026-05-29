import json

from asgiref.sync import async_to_sync
from chat.models import MyChats
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
import datetime
class MychatApp(AsyncJsonWebsocketConsumer):

    async def connect(self):
        print("CONNECTED")
        await self.accept()
        await self.channel_layer.group_add(f"mychat_app{self.scope['user']}",self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        text_data =json.loads(text_data)
        await self.channel_layer.group_send(f"mychat_app{text_data['user']}",
                                            
                                            { 
                                                "type" : "send_msg",
                                                "msg": text_data['msg']
                                            }
                                            )
        await self.save_chat(text_data)

    @database_sync_to_async
    def save_chat(self, text_data):

        frnd = User.objects.get(username=text_data['user'])

        # MY CHAT
        mychats, created = MyChats.objects.get_or_create(
            me=self.scope['user'],
            frnd=frnd
        )

        old_chats = mychats.chats or {}

        old_chats[str(datetime.datetime.now())] = {
            'user': 'me',
            'msg': text_data['msg']
        }

        mychats.chats = old_chats

        mychats.save()

        # FRIEND CHAT
        mychats, created = MyChats.objects.get_or_create(
            me=frnd,
            frnd=self.scope['user']
        )

        old_chats = mychats.chats or {}

        old_chats[str(datetime.datetime.now())] = {
            'user': self.scope['user'].username,
            'msg': text_data['msg']
        }

        mychats.chats = old_chats

        mychats.save()

    async def send_msg(self,event):
        print(event)
        await self.send(text_data=event['msg'])

    async def disconnect(self, close_code):
    
        print("DISCONNECTED")
