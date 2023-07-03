import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
from django_redis import get_redis_connection

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.roomGroupName = f"group_chat_{self.user.id}"
        self.roomName = self.scope['url_route']['kwargs']['room_name']
        self.roomGroup = f"group_chat_{self.roomName}"
        self.redis = get_redis_connection()

        await self.channel_layer.group_add(
            self.roomGroupName,
            self.channel_name
        )
        await self.channel_layer.group_add(
            self.roomGroup,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.roomGroupName,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            self.roomGroup,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message")
        file_data = text_data_json.get("file_data")

        if message:
            await self.channel_layer.group_send(
                self.roomGroup, {
                    "type": "send_message",
                    "message": message,
                }
            )
            # Save the message in Redis with an expiration time of 10 minutes
            self.redis.setex('chat_message', 600, message)
        elif file_data:
            await self.channel_layer.group_send(
                self.roomGroup, {
                    "type": "send_file",
                    "file_data": file_data,
                }
            )

    async def send_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            "message": message,
            "is_file": False
        }))

    async def send_file(self, event):
        file_data = event["file_data"]
        await self.send(text_data=json.dumps({
            "file_data": file_data,
            "is_file": True
        }))

    async def joinRoom(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
