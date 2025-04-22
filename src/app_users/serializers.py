from rest_framework import serializers
from .models import CustomUser, Profile


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'is_active', 'is_staff', 'is_superuser', 'created_at']


class ProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Profile
        fields = ['id', 'user', 'name', 'avatar', 'bio', 'global_name', 'status', 'created_at', 'updated_at']



