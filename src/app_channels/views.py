import json
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app_auth.base_auth import CookieJWTAuthentication
from app_auth.livekit_utils import generate_livekit_token
from livekit import api

from app_users.models import Profile
from app_servers.models import Server

from .serializers import ChannelSerializer
from .utils import get_or_create_dm_channel
from .models import Channel


class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    authentication_classes = [CookieJWTAuthentication]

    def get_queryset(self):
        profile = self.request.user.profile
        # Каналы, где пользователь участник ИЛИ публичные каналы на серверах, где он участник
        return Channel.objects.filter(
            models.Q(participants=profile) |
            models.Q(is_private=False, server__members__profile=profile)
        ).distinct()

    @action(detail=False, methods=["post"], url_path="dm")
    def create_dm(self, request):
        target_user_id = request.data.get("target_user_id")
        if not target_user_id:
            return Response({'error': 'target_user_id is required'}, status=400)

        try:
            current = request.user.profile
            target = Profile.objects.get(id=target_user_id)
        except Profile.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        channel = get_or_create_dm_channel(current, target)
        serializer = self.get_serializer(channel)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="livekit-token")
    def livekit_token(self, request, pk=None):
        user = request.user
        try:
            channel = self.get_object()
        except Channel.DoesNotExist:
            return Response({"error": "Channel not found"}, status=status.HTTP_404_NOT_FOUND)

        # Проверка членства в канале
        if not channel.participants.filter(user=user.profile.user).exists():
            return Response({"error": "You are not a participant of this channel"}, status=status.HTTP_403_FORBIDDEN)

        room_name = str(channel.id)
        identity = str(user.id)

        video_grants = api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True
        )

        metadata = {
            "name": user.profile.name,
            "avatar": request.build_absolute_uri(user.profile.avatar.url) if user.profile.avatar else None
        }

        token = generate_livekit_token(
            identity=identity,
            channel_id=room_name,
            video_grants=video_grants,
            metadata=json.dumps(metadata)
        )

        return Response({
            "token": token,
            "roomName": room_name
        })
