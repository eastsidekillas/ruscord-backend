from rest_framework import serializers
from .models import Friend, FriendRequest
from app_users.serializers import UserSerializer


class FriendSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = Friend
        fields = ['id', 'sender', 'receiver', 'created_at']
        read_only_fields = ['created_at']


class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at']
        read_only_fields = ['created_at']
