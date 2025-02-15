import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from api.middleware import JWTAuthMiddleware
from api.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        ),
    }
)
