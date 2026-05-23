from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.exceptions import AuthenticationFailed

from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from urllib.parse import parse_qs
from app_users.models import CustomUser


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_params = parse_qs(scope.get("query_string", b"").decode())
        token = query_params.get('token', [None])[0]

        if token:
            try:
                access_token = AccessToken(token)
                user = await self.get_user_from_token(access_token['user_id'])
                scope['user'] = user or AnonymousUser()
            except Exception as e:
                print(f"WS token error: {e}")
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, user_id):
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return None


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('access_token')
        if not token:
            raise AuthenticationFailed({
                "message": "401: Unauthorized",
                "code": 0
            })

        try:
            access_token = AccessToken(token)
        except Exception:
            raise AuthenticationFailed({
                "message": "Токен просрочен",
                "code": 0
            })

        return self.get_user_from_token(access_token)

    def get_user_from_token(self, access_token):
        try:
            user = self.get_user(access_token)
            return user, access_token
        except Exception as e:
            raise AuthenticationFailed({
                "message": f'Невозможно извлечь пользователя из токена: {str(e)}',
                "code": 0
            })
