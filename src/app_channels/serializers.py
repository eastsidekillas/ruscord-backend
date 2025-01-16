from rest_framework import serializers
from .models import Channel
from app_users.serializers import UserSerializer


class ChannelSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Channel
        fields = ['uuid', 'members', 'created_at']
