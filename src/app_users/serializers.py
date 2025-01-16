# serializers.py
from rest_framework import serializers
from django.conf import settings
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone', 'avatar', 'bio', 'created_at']
        read_only_fields = ['created_at']
