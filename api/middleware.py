import jwt
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.backends import TokenBackend


@database_sync_to_async
def get_user(jwt_token_key):
    try:
        valid_data = jwt.decode(
            jwt=jwt_token_key, key=settings.SECRET_KEY, algorithms="HS256"
        )
        user = get_user_model().objects.get(id=valid_data["user_id"])
        return user
    except ObjectDoesNotExist:
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope["headers"])
        if b"authorization" in headers:
            jwt_token_name, jwt_token_key = headers[b"authorization"].decode().split()
            if jwt_token_name == "Bearer":
                scope["user"] = await get_user(jwt_token_key)
        return await super().__call__(scope, receive, send)
