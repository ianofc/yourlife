from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Corrigido de .as_async() para .as_asgi()
    re_path(r'ws/talkio/(?P<room_name>\w+)/$', consumers.TalkioConsumer.as_asgi()),
]
