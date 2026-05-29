import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import datetime

class MychatApp(AsyncWebsocketConsumer):

    async def connect(self):
        # Use username for consistent group naming
        self.username = self.scope['user'].username
        self.user_group_name = f"mychat_app_{self.username}"
        
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"✓ User {self.username} connected to group {self.user_group_name}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            recipient_username = data.get('user')
            message = data.get('msg')
            
            if not recipient_username or not message:
                print(f"⚠ Invalid message format from {self.username}")
                return
            
            # Send to recipient's group
            recipient_group = f"mychat_app_{recipient_username}"
            sender_username = self.username
            
            print(f"📤 {self.username} → {recipient_username}: {message}")
            
            await self.channel_layer.group_send(
                recipient_group,
                {
                    "type": "send_msg",
                    "msg": message,
                    "sender": sender_username
                }
            )
            
            # Save chat
            await self.save_chat(data)
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
        except Exception as e:
            print(f"❌ Error in receive: {e}")

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
            print(f"✓ Chat saved for {self.username} ↔ {text_data['user']}")
        except User.DoesNotExist:
            print(f"❌ User {text_data['user']} not found")
        except Exception as e:
            print(f"❌ Error saving chat: {e}")

    async def send_msg(self, event):
        """Called when group_send is triggered with type: 'send_msg'"""
        print(f"📥 Sending to {self.username}: {event['msg']} from {event.get('sender', '?')}")
        
        # Send as JSON to client
        await self.send(text_data=json.dumps({
            "msg": event['msg'],
            "sender": event.get('sender', 'Unknown')
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
        print(f"✗ User {self.username} disconnected from group {self.user_group_name}")