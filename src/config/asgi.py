"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()

# import os
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.core.asgi import get_asgi_application
# from channels.auth import AuthMiddlewareStack
# from yourapp import routing  # WebSocket 경로 설정
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yourproject.settings')
#
# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             routing.websocket_urlpatterns
#         )
#     ),
# })
