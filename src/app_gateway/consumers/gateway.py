import os
import redis.asyncio as aioredis
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from app_gateway.utils.status import set_user_status, set_user_offline
from app_users.models import Profile
from app_friends.models import Friend

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

redis_client = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


class GatewayConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
            return

        self.user_id = str(user.id)

        await self.register_session()
        await self.channel_layer.group_add("all_users", self.channel_name)
        await self.accept()

        await set_user_status(user.id, "online")

        await self.channel_layer.group_send(
            "all_users",
            {"type": "user_status_update", "userId": self.user_id, "status": "online"}
        )

        friends = await self.get_friends(user.id)
        for friend in friends:
            friend_user_id = str(friend.user_id)
            friend_status = await self.get_user_session_status(friend_user_id)
            await self.send_json({
                "op": "STATUS_UPDATE",
                "userId": friend_user_id,
                "status": friend_status
            })

    async def disconnect(self, close_code):
        user = self.scope["user"]

        if user.is_authenticated:
            await self.unregister_session()
            await self.channel_layer.group_discard("all_users", self.channel_name)
            await set_user_offline(user.id)

            await self.channel_layer.group_send(
                "all_users",
                {"type": "user_status_update", "userId": self.user_id, "status": "offline"}
            )

    async def receive_json(self, content):
        op = content.get("op")
        data = content.get("d") or {}

        if op == "STATUS_UPDATE":
            new_status = data.get("status")
            if new_status:
                await set_user_status(self.scope["user"].id, new_status)
                await self.set_user_session_status(self.user_id, new_status)

                await self.channel_layer.group_send(
                    "all_users",
                    {"type": "user_status_update", "userId": self.user_id, "status": new_status}
                )
        elif op in ("call.request", "call.response", "call.ended"):
            await self.handle_call_relay(content)

    async def user_status_update(self, event):
        await self.send_json({
            "op": "STATUS_UPDATE",
            "userId": event["userId"],
            "status": event["status"]
        })

    async def handle_call_relay(self, content):
        to_user_id = str(content.get("to_user_id", ""))
        if not to_user_id:
            return
        payload = {**content, "sender_id": self.user_id}
        target_channel = await redis_client.get(f"user:{to_user_id}:channel")
        if target_channel:
            await self.channel_layer.send(
                target_channel.decode(),
                {"type": "call_relay", **payload},
            )

    async def call_relay(self, event):
        await self.send_json({k: v for k, v in event.items() if k != "type"})

    async def register_session(self):
        await redis_client.set(f"user:{self.user_id}:channel", self.channel_name)
        await redis_client.set(f"user:{self.user_id}:status", "online")

    async def unregister_session(self):
        await redis_client.delete(f"user:{self.user_id}:channel")
        await redis_client.delete(f"user:{self.user_id}:status")

    async def get_user_session_status(self, user_id):
        status_bytes = await redis_client.get(f"user:{user_id}:status")
        return status_bytes.decode() if status_bytes else "offline"

    async def set_user_session_status(self, user_id, status):
        await redis_client.set(f"user:{user_id}:status", status)

    async def get_friends(self, user_id):
        return await database_sync_to_async(self.get_user_friends)(user_id)

    def get_user_friends(self, user_id):
        user_profile = Profile.objects.get(user_id=user_id)
        friends = Friend.objects.filter(sender=user_profile) | Friend.objects.filter(receiver=user_profile)
        return [friend.receiver if friend.sender == user_profile else friend.sender for friend in friends]