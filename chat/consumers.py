# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import datetime

class MychatApp(AsyncWebsocketConsumer):

    async def connect(self):
        # Use username for consistent group naming
        self.user_group_name = f"mychat_app_{self.scope['user'].username}"
        
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"User {self.scope['user'].username} connected to group {self.user_group_name}")

    async def receive(self, text_data):
        try:
            text_data = json.loads(text_data)
            recipient_username = text_data.get('user')
            message = text_data.get('msg')
            
            if not recipient_username or not message:
                await self.send(text_data=json.dumps({
                    "error": "Missing user or msg field"
                }))
                return
            
            # Send to recipient's group
            recipient_group = f"mychat_app_{recipient_username}"
            
            await self.channel_layer.group_send(
                recipient_group,
                {
                    "type": "send_msg",
                    "msg": message,
                    "sender": self.scope['user'].username
                }
            )
            
            # Save chat
            await self.save_chat(text_data)
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "error": "Invalid JSON"
            }))

    @database_sync_to_async
    def save_chat(self, text_data):
        from chat.models import MyChats
        from django.contrib.auth.models import User
        
        try:
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
        except User.DoesNotExist:
            print(f"User {text_data['user']} not found")

    async def send_msg(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "msg": event['msg'],
            "sender": event['sender']
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
        print(f"User disconnected from group {self.user_group_name}")