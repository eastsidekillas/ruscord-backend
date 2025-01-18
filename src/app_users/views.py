from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import CustomUser
from django.db import models
from django.db.models import Q
from app_friends.models import Friend, FriendRequest
from .serializers import UserSerializer, RegisterSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='profile')
    def profile(self, request):
        user = self.request.user
        serializer = self.get_serializer(user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['put'], url_path='profile_edit')
    def update_profile(self, request):
        user = self.request.user
        serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()  # Здесь данные должны быть обновлены
            return Response(serializer.data)  # Возвращаем обновленные данные
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        username = request.query_params.get('username', None)
        page = request.query_params.get('page', 1)  # Получаем параметр страницы
        page_size = 10  # Размер страницы, например, 10 пользователей на страницу

        if username:
            # Исключаем текущего пользователя из поиска
            users = CustomUser.objects.exclude(id=request.user.id).filter(username__icontains=username)

            # Получаем список пользователей, с которыми есть активные заявки (отправленные или полученные)
            sent_requests = FriendRequest.objects.filter(from_user=request.user).values_list('to_user', flat=True)
            received_requests = FriendRequest.objects.filter(to_user=request.user).values_list('from_user', flat=True)
            friends = Friend.objects.filter(
                models.Q(sender=request.user) | models.Q(receiver=request.user)
            ).values_list('receiver', flat=True)

            # Исключаем пользователей, с которыми есть заявки или которые уже являются друзьями
            users = users.exclude(id__in=sent_requests)  # Исключаем тех, кому мы отправили заявку
            users = users.exclude(id__in=received_requests)  # Исключаем тех, кто нам отправил заявку
            users = users.exclude(id__in=friends)  # Исключаем уже добавленных друзей

            # Пагинация
            start = (int(page) - 1) * page_size
            end = start + page_size
            users = users[start:end]  # Загружаем пользователей только на текущей странице

            serializer = self.get_serializer(users, many=True)
            return Response(serializer.data)

        return Response([])

class UserRegisterViewSet(APIView):

    def post(self, request, *args, **kwargs):
        # Используем сериализатор для регистрации нового пользователя
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()  # Создаём нового пользователя
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
