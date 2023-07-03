import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.cache import cache


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        # Request cached messages on connection open
        self.send_cached_messages()

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command', None)

        if command == 'fetch_messages':
            self.send_cached_messages()
        elif command == 'send_message':
            message = data['message']
            self.save_and_send_message(message)
        elif command == 'send_file':
            file_data = data['file_data']
            caption = data['caption']
            self.save_and_send_file(file_data, caption)

    def send_message(self, message, is_file=False, caption=None):
        if is_file:
            self.send(text_data=json.dumps({
                'message': message,
                'is_file': True,
                'caption': caption
            }))
        else:
            self.send(text_data=json.dumps({
                'message': message,
                'is_file': False
            }))

    def save_and_send_message(self, message):
        # Save message to cache
        self.save_message_to_cache(message)

        # Broadcast the message to the room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'send.message',
                'message': message
            }
        )

    def save_and_send_file(self, file_data, caption):
        # Save file and caption to cache
        self.save_message_to_cache(file_data)
        self.save_message_to_cache(caption)

        # Broadcast the file and caption to the room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'send.file',
                'file_data': file_data,
                'caption': caption
            }
        )

    def send_cached_messages(self):
        cached_messages = self.get_cached_messages()
        for message in cached_messages:
            self.send(text_data=message)

    def save_message_to_cache(self, message):
        cached_messages = cache.get(self.room_group_name, [])
        cached_messages.append(message)
        cache.set(self.room_group_name, cached_messages, 600)  # Set cache expiration to 10 minutes

    def get_cached_messages(self):
        return cache.get(self.room_group_name, [])

    # Receive message from room group
    def send_message(self, event):
        message = event['message']
        self.send_message(message)

    # Receive file and caption from room group
    def send_file(self, event):
        file_data = event['file_data']
        caption = event['caption']
        self.send_message(file_data, is_file=True, caption=caption)
