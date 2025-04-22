from django.db import models
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.conf import settings
import uuid

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from ruscord.utils import build_absolute_uri
from app_auth.base_auth import CookieJWTAuthentication
from app_channels.serializers import ChannelSerializer
from app_channels.models import Channel

from .serializers import ServerSerializer, MemberSerializer, InviteLinkSerializer
from .models import Server, Member, InviteLink


class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    authentication_classes = [CookieJWTAuthentication]

    def get_queryset(self):
        # Отображаем серверы, где пользователь является участником
        profile = self.request.user.profile
        return Server.objects.filter(members__profile=profile)

    def perform_create(self, serializer):
        profile = self.request.user.profile
        avatar = self.request.FILES.get('avatar')
        server = serializer.save(owner=profile)

        server = serializer.save(owner=profile, avatar=avatar)

        # Добавляем владельца как участника
        Member.objects.create(profile=profile, server=server)

        # Создаем текстовый канал
        text_channel = Channel.objects.create(
            server=server,
            name='general',
            channel_type=Channel.TEXT,
            scope=Channel.GROUP,
            owner=profile,
            is_private=False
        )

        # Создаем голосовой канал
        audio_channel = Channel.objects.create(
            server=server,
            name='Voice Channel',
            channel_type=Channel.AUDIO,
            scope=Channel.GROUP,
            owner=profile,
            is_private=False
        )

        # Добавляем владельца в оба канала
        text_channel.participants.add(profile)
        audio_channel.participants.add(profile)

        return Response({
            'id': server.id,
            'default_channel_id': text_channel.id
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='channels')
    def get_server_channels(self, request, pk=None):
        server = self.get_object()
        channels = server.channels.all()
        serializer = ChannelSerializer(channels, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='join')
    def join_server(self, request, pk=None):
        profile = request.user.profile
        server = self.get_object()

        member, created = Member.objects.get_or_create(profile=profile, server=server)

        # Присоединяем к публичным каналам
        public_channels = server.channels.filter(is_private=False)
        for channel in public_channels:
            channel.participants.add(profile)

        return Response({'message': 'Successfully joined server'})

    @action(detail=True, methods=['get'], url_path='members')
    def list_members(self, request, pk=None):
        server = self.get_object()
        members = Member.objects.filter(server=server)
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='invite')
    def invite_member(self, request, pk=None):
        server = self.get_object()
        profile_id = request.data.get('profile_id')
        if not profile_id:
            return Response({'error': 'profile_id is required'}, status=400)

        try:
            profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        member, created = Member.objects.get_or_create(server=server, profile=profile)

        # Добавляем участника в публичные каналы
        for channel in server.channels.filter(is_private=False):
            channel.participants.add(profile)

        return Response({'message': f"{profile.name} invited successfully!"})


class ServerInviteCreateView(APIView):
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request, pk=None):
        server = get_object_or_404(Server, pk=pk)
        profile = request.user.profile

        max_uses = request.data.get('max_uses')
        expires_in_minutes = request.data.get('expires_in')

        expires_at = None
        if expires_in_minutes:
            expires_at = timezone.now() + timezone.timedelta(minutes=int(expires_in_minutes))

        invite = InviteLink.objects.create(
            server=server,
            creator=profile,
            max_uses=max_uses,
            expires_at=expires_at
        )

        return Response({'invite_token': invite.token})


class ServerInviteJoinView(APIView):
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request, token=None):
        invite = get_object_or_404(InviteLink, token=token)

        if not invite.is_valid():
            return Response({'error': 'Invite link expired or exceeded usage'}, status=400)

        server = invite.server
        profile = request.user.profile

        Member.objects.get_or_create(server=server, profile=profile)

        public_channels = server.channels.filter(is_private=False)

        for channel in public_channels:
            channel.participants.add(profile)

        invite.uses += 1
        invite.save()

        # Возвращаем ID сервера и дефолтного канала (например, самого первого публичного)
        default_channel = public_channels.first()

        return Response({
            'message': f'You have joined {server.name}',
            'server_id': server.id,
            'default_channel_id': default_channel.id if default_channel else None
        })


class ServerInviteDetailsView(APIView):
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request, token=None):
        invite = get_object_or_404(InviteLink, token=token)

        if not invite.is_valid():
            raise NotFound(detail="Invite link expired or exceeded usage")

        server = invite.server

        server_avatar = server.avatar.url if server.avatar else None
        if server_avatar:
            # Для формирования абсолютного URL используем build_absolute_uri
            avatar_url = request.build_absolute_uri(server_avatar)
        else:
            avatar_url = None

        response_data = {
            'server_name': server.name,
            'server_avatar': avatar_url,
            'server_description': server.description,
            'invite_token': invite.token,
            'expires_at': invite.expires_at,
            'max_uses': invite.max_uses,
            'current_uses': invite.uses,
        }

        return Response(response_data)