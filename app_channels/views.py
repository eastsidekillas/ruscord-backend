from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DirectMessageChannel
from .serializers import DirectMessageChannelSerializer
from app_users.models import CustomUser


class DirectMessageChannelViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def get_or_create_channel(self, request):
        """Создать или получить существующий личный чат"""
        user = request.user
        recipient_id = request.data.get('recipient_id')

        if not recipient_id:
            return Response({"detail": "Не указан recipient_id"}, status=status.HTTP_400_BAD_REQUEST)

        recipient = CustomUser.objects.filter(id=recipient_id).first()
        if not recipient:
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Ищем существующий канал
        channel = DirectMessageChannel.objects.filter(members=user).filter(members=recipient).first()

        # Если канал не найден, создаем новый
        if not channel:
            channel = DirectMessageChannel.objects.create()
            channel.members.add(user, recipient)

        serializer = DirectMessageChannelSerializer(channel)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def my_channels(self, request):
        """Получить все чаты текущего пользователя"""
        channels = DirectMessageChannel.objects.filter(members=request.user)
        serializer = DirectMessageChannelSerializer(channels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
