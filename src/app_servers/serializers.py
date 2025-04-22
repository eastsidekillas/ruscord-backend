from rest_framework import serializers
from app_users.serializers import ProfileSerializer
from .models import Server, Member, InviteLink
from app_channels.models import Channel


class MemberSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = Member
        fields = ['id', 'profile', 'joined_at']


class ServerSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    default_channel_id = serializers.SerializerMethodField()

    class Meta:
        model = Server
        fields = ['id', 'name', 'description', 'avatar', 'owner', 'created_at', 'default_channel_id']
        read_only_fields = ['id', 'owner', 'created_at', 'default_channel_id']

    def get_default_channel_id(self, server):
        # Попытаемся получить ID первого текстового канала "general"
        general_channel = server.channels.filter(name='general', channel_type=Channel.TEXT).first()
        if general_channel:
            return general_channel.id
        # Если "general" не найден, возвращаем ID любого первого канала (если есть)
        first_channel = server.channels.first()
        return first_channel.id if first_channel else None


class InviteLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = InviteLink
        fields = ['token', 'server', 'creator', 'max_uses', 'uses', 'expires_at', 'created_at']
        read_only_fields = ['token', 'creator', 'uses', 'created_at']