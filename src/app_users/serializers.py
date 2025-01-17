from rest_framework import serializers
from django.contrib.auth.models import User
from django.conf import settings
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone', 'avatar', 'bio', 'created_at']
        read_only_fields = ['created_at']

    def update(self, instance, validated_data):
        # Здесь можно добавить дополнительные шаги при обновлении, если это необходимо
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user
