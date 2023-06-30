from django.urls import path, re_path
from .consumers import ChatConsumer

# Here, "" is routing to the URL ChatConsumer which
# will handle the chat functionality.
websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
    # Add a route for the root path
    path("", ChatConsumer.as_asgi()),
]
