from rest_framework import serializers
from .models import Friendship
from .models import DirectMessage
from app_users.serializers import UserSerializer


class FriendshipSerializer(serializers.ModelSerializer):
    requester = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = Friendship
        fields = ['id', 'requester', 'receiver', 'status', 'created_at']
        read_only_fields = ['created_at', 'requester', 'receiver']


class FriendshipRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ['receiver']  # Только получатель


class FriendshipUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ['status']  # Только статус


class DirectMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = DirectMessage
        fields = ['id', 'sender', 'receiver', 'content', 'created_at', 'edited_at']
        read_only_fields = ['id', 'sender', 'receiver', 'created_at', 'edited_at']


class DirectMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectMessage
        fields = ['receiver', 'content']  # Только получатель и контент
