from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app_auth.base_auth import CookieJWTAuthentication

from app_users.models import Profile


from .serializers import ChannelSerializer
from .utils import get_or_create_dm_channel
from .models import Channel


class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

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

