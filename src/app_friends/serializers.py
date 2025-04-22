from rest_framework import serializers
from .models import Friend, FriendRequest
from app_users.serializers import ProfileSerializer


class FriendSerializer(serializers.ModelSerializer):
    sender = ProfileSerializer(read_only=True)
    receiver = ProfileSerializer(read_only=True)

    class Meta:
        model = Friend
        fields = ['id', 'sender', 'receiver']


class FriendRequestSerializer(serializers.ModelSerializer):
    to_user = ProfileSerializer()

    class Meta:
        model = FriendRequest
        fields = ['id', 'to_user', 'status', 'created_at']
