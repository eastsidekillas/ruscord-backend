from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Friendship, DirectMessage
from .serializers import (
    FriendshipSerializer,
    FriendshipRequestSerializer,
    FriendshipUpdateSerializer,
    DirectMessageSerializer,
    DirectMessageCreateSerializer
)


class FriendshipViewSet(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Показываем только заявки, которые связаны с текущим пользователем
        user = self.request.user
        return Friendship.objects.filter(requester=user) | Friendship.objects.filter(receiver=user)

    @action(detail=False, methods=['post'])
    def send_request(self, request):
        """Отправка запроса в друзья"""
        serializer = FriendshipRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(requester=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Обновление статуса заявки (принять/отклонить)"""
        friendship = self.get_object()
        if friendship.receiver != request.user:
            return Response({'detail': 'Недостаточно прав.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = FriendshipUpdateSerializer(friendship, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def pending_requests(self, request):
        """Просмотр ожидающих запросов в друзья"""
        pending = Friendship.objects.filter(receiver=request.user, status='pending')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def friends(self, request):
        """Получение списка друзей"""
        friends = Friendship.objects.filter(
            (models.Q(requester=request.user) | models.Q(receiver=request.user)) & models.Q(status='accepted')
        )
        serializer = self.get_serializer(friends, many=True)
        return Response(serializer.data)


class DirectMessageViewSet(viewsets.ModelViewSet):
    queryset = DirectMessage.objects.all()
    serializer_class = DirectMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Возвращает только сообщения между текущим пользователем и другим пользователем."""
        user = self.request.user
        receiver_id = self.request.query_params.get('receiver')
        if receiver_id:
            return DirectMessage.objects.filter(
                (models.Q(sender=user, receiver_id=receiver_id) |
                 models.Q(sender_id=receiver_id, receiver=user))
            ).order_by('-created_at')
        return DirectMessage.objects.none()

    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """Отправка личного сообщения"""
        serializer = DirectMessageCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)