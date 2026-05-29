from django.urls import path
from chat.consumers import MychatApp

websocket_urlpatterns = [
    path('ws/wsc/',MychatApp.as_asgi())
]