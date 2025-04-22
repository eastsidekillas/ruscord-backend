from channels.generic.websocket import AsyncJsonWebsocketConsumer
from app_gateway.utils.status import set_user_status, set_user_offline, get_user_status
from app_users.models import Profile
from app_friends.models import Friend
from channels.db import database_sync_to_async


class GatewayConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
        else:
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
                friend_status = await get_user_status(friend.id)
                await self.send_json({
                    "op": "STATUS_UPDATE",
                    "userId": friend.id,
                    "status": friend_status
                })

    async def disconnect(self, close_code):
        user = self.scope["user"]

        if user.is_authenticated:
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

                # Отправляем обновление статуса всем подключенным пользователям
                await self.channel_layer.group_send(
                    "all_users",
                    {
                        "type": "user_status_update",
                        "userId": self.scope["user"].id,
                        "status": new_status
                    }
                )

    async def get_friends(self, user_id):
        # Получаем список друзей пользователя
        friends = await database_sync_to_async(self.get_user_friends)(user_id)
        return friends

    def get_user_friends(self, user_id):
        # Логика получения списка друзей пользователя
        user_profile = Profile.objects.get(user_id=user_id)
        friends = Friend.objects.filter(sender=user_profile) | Friend.objects.filter(receiver=user_profile)
        return [friend.sender if friend.sender.id != user_id else friend.receiver for friend in friends]
