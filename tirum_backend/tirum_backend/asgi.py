"""
ASGI config for tirum_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information, see:
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import User.routing  # Replace with your actual app name

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tirum_backend.settings')

django.setup()

application = ProtocolTypeRouter({
    # Handles HTTP requests
    "http": django.core.asgi.get_asgi_application(),

    # Handles WebSocket connections
    "websocket": AuthMiddlewareStack(
        URLRouter(
            User.routing.websocket_urlpatterns
        )
    ),
})
