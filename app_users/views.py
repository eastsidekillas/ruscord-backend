from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import UserSerializer


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