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
        # Извлекаем токен из query string
        query_params = parse_qs(scope.get("query_string", b"").decode())
        token = query_params.get('token', [None])[0]

        if token:
            try:
                # Проверяем токен с помощью SimpleJWT
                access_token = AccessToken(token)
                user_id = access_token['user_id']

                # Получаем пользователя из базы данных
                user = await self.get_user_from_token(user_id)
                if user:
                    scope['user'] = user
                else:
                    scope['user'] = AnonymousUser()  # Пользователь не найден, анонимный
            except Exception as e:
                print(f"Error during token processing: {str(e)}")
                scope['user'] = AnonymousUser()  # Ошибка в обработке токена, анонимный пользователь
        else:
            scope['user'] = AnonymousUser()  # Нет токена, анонимный пользователь

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, user_id):
        try:
            # Получаем пользователя по ID
            user = CustomUser.objects.get(id=user_id)
            return user
        except CustomUser.DoesNotExist:
            return None  # Если пользователь не найден, возвращаем None


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Извлекаем токен из cookies
        token = request.COOKIES.get('access_token')
        if not token:
            raise AuthenticationFailed({
                "message": "401: Unauthorized",
                "code": 0
            })

        try:
            # Проверка токена с помощью стандартного механизма JWT
            access_token = AccessToken(token)
        except Exception:
            raise AuthenticationFailed({
                "message": "Токен просрочен",
                "code": 0
            })

        # делаем возврат пользователя
        return self.getUser_from_token(access_token)

    def getUser_from_token(self, access_token):
        try:
            user = self.get_user(access_token)
            return user, access_token
        except Exception as e:
            raise AuthenticationFailed({
                "message": f'Невозможно извлечь пользователя из токена: {str(e)}',
                "code": 0
            })
