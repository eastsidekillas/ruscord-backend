from rest_framework import serializers
from django.utils.timezone import localtime
from django.utils import formats
from .models import CustomUser


class CustomDateField(serializers.Field):
    def to_representation(self, value):
        if value:
            value = localtime(value)
            return formats.date_format(value, "d E Yг.")
        return None


class UserSerializer(serializers.ModelSerializer):
    created_at = CustomDateField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone', 'avatar', 'bio', 'created_at']

