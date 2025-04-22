from rest_framework import serializers
from .models import Messages
from app_users.serializers import ProfileSerializer


class DirectMessageSerializer(serializers.ModelSerializer):
    sender = ProfileSerializer(read_only=True)

    class Meta:
        model = Messages
        fields = ['id', 'channel', 'sender', 'content', 'file_url', 'deleted', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']
