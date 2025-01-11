from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Channel
from .serializers import ChannelSerializer
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
        channel = Channel.objects.filter(members=user).filter(members=recipient).first()

        # Если канал не найден, создаем новый
        if not channel:
            channel = Channel.objects.create()
            channel.members.add(user, recipient)

        serializer = ChannelSerializer(channel)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def my_channels(self, request):
        """Получить все чаты текущего пользователя"""
        channels = Channel.objects.filter(members=request.user)
        serializer = ChannelSerializer(channels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def channel_info(self, request, pk=None):
        """Получить информацию о канале по UUID"""
        try:
            # Находим канал по UUID
            channel = Channel.objects.get(uuid=pk)
        except Channel.DoesNotExist:
            return Response({"detail": "Канал не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Сериализуем канал
        serializer = ChannelSerializer(channel)
        return Response(serializer.data, status=status.HTTP_200_OK)