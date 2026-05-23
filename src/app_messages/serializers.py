from rest_framework import serializers
from .models import Messages
from app_users.serializers import ProfileSerializer


class ReplyPreviewSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Messages
        fields = ['id', 'content', 'sender_name']

    def get_sender_name(self, obj):
        return obj.sender.name


class ForwardPreviewSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Messages
        fields = ['id', 'content', 'sender_name']

    def get_sender_name(self, obj):
        return obj.sender.name


class DirectMessageSerializer(serializers.ModelSerializer):
    sender = ProfileSerializer(read_only=True)
    reply_to = ReplyPreviewSerializer(read_only=True)
    forwarded_from = ForwardPreviewSerializer(read_only=True)

    class Meta:
        model = Messages
        fields = [
            'id', 'channel', 'sender', 'content', 'file_url',
            'deleted', 'created_at', 'reply_to', 'forwarded_from',
        ]
        read_only_fields = ['id', 'sender', 'created_at']