from django.urls import re_path

from docker_demo.apps.realtime.consumers import PassiveAggressiveConsumer

websocket_urlpatterns = [
    re_path(r"back/ws/hello/$", PassiveAggressiveConsumer.as_asgi()),
]
