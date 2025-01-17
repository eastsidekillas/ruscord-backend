from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Friend, FriendRequest
import uuid
from app_users.models import CustomUser
from .serializers import UserSerializer, FriendRequestSerializer, FriendSerializer


# Вьюсет для работы с пользователями и заявками в друзья
class FriendViewSet(viewsets.ModelViewSet):
    queryset = Friend.objects.all()
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def send_request(self, request, pk=None):
        """Отправить заявку в друзья"""
        to_user = CustomUser.objects.get(pk=pk)

        if request.user.id == to_user.id:
            return Response({"detail": "Нельзя добавить себя в друзья."}, status=status.HTTP_400_BAD_REQUEST)

        if FriendRequest.objects.filter(
                from_user=request.user,
                to_user=to_user
        ).exists() or FriendRequest.objects.filter(
            from_user=to_user, to_user=request.user
        ).exists():
            return Response({"detail": "Заявка уже отправлена"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            friend_request = FriendRequest.objects.create(from_user=request.user, to_user=to_user)
            serializer = FriendRequestSerializer(friend_request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='accept_request/(?P<request_id>[^/.]+)')
    def accept_request(self, request, pk=None, request_id=None):
        """Принять заявку в друзья"""
        # Преобразуем request_id в UUID
        from_user_id = request_id  # request_id это UUID
        try:
            from_user_uuid = uuid.UUID(from_user_id)  # Преобразуем в объект UUID
        except ValueError:
            return Response({"detail": "Неверный формат ID пользователя."}, status=status.HTTP_400_BAD_REQUEST)

        # Ищем заявку по request_id и пользователю (pk)
        friend_request = FriendRequest.objects.filter(
            to_user=request.user,  # Получатель заявки (тот, кто принимает)
            from_user__id=from_user_uuid,  # Используем UUID для поиска
            status='pending'  # Только заявки в ожидании
        ).first()

        if not friend_request:
            return Response({"detail": "Заявка не найдена или уже обработана."}, status=status.HTTP_404_NOT_FOUND)

        # Обновляем статус заявки на "принято"
        friend_request.status = 'accepted'
        friend_request.save()

        # Создаем связь "друг"
        Friend.objects.create(sender=friend_request.from_user, receiver=friend_request.to_user)

        # Возвращаем информацию о созданной связи
        serializer = FriendSerializer(
            Friend.objects.filter(sender=friend_request.from_user, receiver=friend_request.to_user).first())

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def reject_request(self, request, pk=None):
        """Отклонить заявку в друзья"""
        friend_request = FriendRequest.objects.filter(to_user=request.user, from_user_id=pk, status='pending').first()
        if not friend_request:
            return Response({"detail": "Заявка не найдена"}, status=status.HTTP_404_NOT_FOUND)

        friend_request.status = 'rejected'
        friend_request.save()
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def remove_friend(self, request, pk=None):
        """Удалить друга"""
        friend = Friend.objects.filter(
            models.Q(sender=request.user, receiver_id=pk) | models.Q(sender_id=pk, receiver=request.user)
        ).first()
        if not friend:
            return Response({"detail": "Друг не найден"}, status=status.HTTP_404_NOT_FOUND)

        friend.delete()
        return Response({"detail": "Друг удален"}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='my_friends')
    def my_friends(self, request):
        friends = Friend.objects.filter(sender=request.user).values('receiver__username')
        return Response(friends)

    @action(detail=False, methods=['get'], url_path='pending_requests')
    def pending_requests(self, request):
        """Получить список всех ожидающих заявок"""
        requests = FriendRequest.objects.filter(to_user=request.user, status='pending')
        serializer = FriendRequestSerializer(requests, many=True)  # Передаем все заявки в сериализатор
        return Response(serializer.data)
