from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from app_users.models import CustomUser
from app_users.models import Profile


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise serializers.ValidationError("Email и пароль обязательны")

        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError("Неверный email или пароль")

        if not user.is_active:
            raise serializers.ValidationError("Этот пользователь был деактивирован")

        return self.get_tokens_for_user(user)

    @staticmethod
    def get_tokens_for_user(user):
        refresh = CustomTokenObtainPairSerializer.get_token(user)
        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh)
        }


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'name']

    def create(self, validated_data):
        name = validated_data.pop('name')
        user = CustomUser.objects.create_user(**validated_data)

        Profile.objects.create(user=user, name=name, global_name=user.username)

        return user
