from rest_framework import serializers
from .models import DirectMessageChannel
from app_users.serializers import UserSerializer


class DirectMessageChannelSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = DirectMessageChannel
        fields = ['uuid', 'members', 'created_at']
