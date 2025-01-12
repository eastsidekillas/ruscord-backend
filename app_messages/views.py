from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Message
from .serializers import MessageSerializer


# Вьюсет для сообщений
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Отправить сообщение"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Отметить сообщение как прочитанное"""
        message = self.get_object()
        if message.recipient != request.user:
            return Response({"detail": "Нет прав для этого действия"}, status=status.HTTP_403_FORBIDDEN)

        message.is_read = True
        message.save()
        return Response({"detail": "Сообщение отмечено как прочитанное"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='history')
    def get_message_history(self, request):
        sender_id = request.query_params.get('sender')
        recipient_id = request.query_params.get('recipient')

        if not sender_id or not recipient_id:
            return Response({"detail": "sender и recipient обязательно"}, status=status.HTTP_400_BAD_REQUEST)

        # Фильтрация сообщений между отправителем и получателем
        messages = Message.objects.filter(
            (models.Q(sender_id=sender_id, recipient_id=recipient_id) |
             models.Q(sender_id=recipient_id, recipient_id=sender_id))
        ).order_by('timestamp')

        # Передаем request в контексте при создании сериализатора
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)