from rest_framework import serializers
from .models import Message
from app_users.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'text', 'timestamp', 'is_read']
        read_only_fields = ['timestamp', 'is_read']
