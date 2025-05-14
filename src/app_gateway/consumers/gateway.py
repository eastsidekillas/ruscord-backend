import os
import redis
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from app_gateway.utils.status import set_user_status, set_user_offline, get_user_status
from app_users.models import Profile
from app_friends.models import Friend
from channels.layers import get_channel_layer
from dotenv import load_dotenv

load_dotenv()

# Получение настроек Redis из переменных окружения
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")  # Значение по умолчанию, если не задано
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


class GatewayConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
        else:
            self.user_id = str(user.id)
            self.channel_name_str = self.channel_name

            # Регистрируем сессию пользователя в Redis
            await self.register_session()

            await self.accept()

            # Устанавливаем статус онлайн
            await set_user_status(user.id, "online")
            await self.send_json({
                "op": "STATUS_UPDATE",
                "userId": user.id,
                "status": "online"
            })

            # Отправка статуса друзьям
            friends = await self.get_friends(user.id)
            for friend in friends:
                # Получаем текущий статус друга
                friend_status = await self.get_user_session_status(str(friend.id))
                await self.send_json({
                    "op": "STATUS_UPDATE",
                    "userId": friend.id,
                    "status": friend_status
                })

    async def disconnect(self, close_code):
        user = self.scope["user"]

        if user.is_authenticated:
            # Удаляем сессию пользователя из Redis
            await self.unregister_session()

            # Устанавливаем статус оффлайн при разрыве соединения
            await set_user_offline(user.id)

            # Отправляем обновление статуса всем подключенным пользователям
            await self.channel_layer.group_send(
                "all_users",
                {
                    "type": "user_status_update",
                    "userId": user.id,
                    "status": "offline"
                }
            )

    async def receive_json(self, content):
        op = content.get("op")
        data = content.get("d")

        if op == "STATUS_UPDATE":
            new_status = data.get("status")
            if new_status:
                await set_user_status(self.scope["user"].id, new_status)
                await self.set_user_session_status(str(self.scope["user"].id), new_status)

                # Отправляем обновление статуса всем подключенным пользователям
                await self.channel_layer.group_send(
                    "all_users",
                    {
                        "type": "user_status_update",
                        "userId": self.scope["user"].id,
                        "status": new_status
                    }
                )

    async def register_session(self):
        # Сохраняем channel_name пользователя в Redis
        redis_client.set(f"user:{self.user_id}:channel", self.channel_name_str)
        # Также можем сохранить статус онлайн при подключении
        redis_client.set(f"user:{self.user_id}:status", "online")

    async def unregister_session(self):
        # Удаляем channel_name пользователя из Redis
        redis_client.delete(f"user:{self.user_id}:channel")
        # Удаляем статус при отключении
        redis_client.delete(f"user:{self.user_id}:status")

    async def get_user_session_channel(self, user_id):
        # Получаем channel_name пользователя из Redis
        channel_name_bytes = redis_client.get(f"user:{user_id}:channel")
        return channel_name_bytes.decode() if channel_name_bytes else None

    async def get_user_session_status(self, user_id):
        # Получаем статус пользователя из Redis (если он там есть)
        status_bytes = redis_client.get(f"user:{user_id}:status")
        return status_bytes.decode() if status_bytes else "offline"  # По умолчанию считаем оффлайн

    async def set_user_session_status(self, user_id, status):
        # Обновляем статус пользователя в Redis
        redis_client.set(f"user:{user_id}:status", status)

    async def get_friends(self, user_id):
        friends = await database_sync_to_async(self.get_user_friends)(user_id)
        return friends

    def get_user_friends(self, user_id):
        user_profile = Profile.objects.get(user_id=user_id)
        friends = Friend.objects.filter(sender=user_profile) | Friend.objects.filter(receiver=user_profile)
        return [friend.sender if friend.sender.id != user_id else friend.receiver for friend in friends]