from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import CustomUser
from .serializers import UserSerializer, RegisterSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='profile')
    def profile(self, request):
        user = self.request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        username = request.query_params.get('username', None)

        if username:
            # исключаем текущего пользователя из поиска
            users = CustomUser.objects.exclude(id=request.user.id).filter(username__icontains=username)
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
