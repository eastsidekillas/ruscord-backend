from rest_framework import serializers
from app_users.serializers import ProfileSerializer
from .models import Channel


class ChannelSerializer(serializers.ModelSerializer):
    participants = ProfileSerializer(many=True, read_only=True)

    class Meta:
        model = Channel
        fields = ['id', 'server', 'name', 'channel_type', 'scope', 'owner', 'participants', 'is_private', 'created_at']
        read_only_fields = ['id', 'created_at', 'server']
