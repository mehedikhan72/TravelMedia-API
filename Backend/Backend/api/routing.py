from django.urls import path
from .consumers import NotificationConsumer

websocket_urlpatterns = [
    path('ws/notification/<str:group_name>/', NotificationConsumer.as_asgi())
]