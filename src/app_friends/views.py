from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from django.db.models import Q
from app_auth.base_auth import CookieJWTAuthentication
from app_friends.serializers import FriendRequestSerializer, FriendSerializer
from app_users.serializers import ProfileSerializer
from app_friends.models import FriendRequest, Friend
from app_users.models import CustomUser, Profile


# Получение друзей пользователя

class GetUserFriends(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProfileSerializer
    authentication_classes = [CookieJWTAuthentication]

    def list(self, request, *args, **kwargs):
        user_profile = request.user.profile
        friends_profiles = []

        friend_relations = Friend.objects.filter(sender=user_profile) | Friend.objects.filter(receiver=user_profile)

        for relation in friend_relations:
            if relation.sender == user_profile:
                friends_profiles.append(relation.receiver)
            else:
                friends_profiles.append(relation.sender)

        unique_friends = list(set(friends_profiles))

        serializer = self.get_serializer(unique_friends, many=True)
        return Response(serializer.data)


# Отправка запроса в друзья
class PostFriendRequest(viewsets.ViewSet):
    authentication_classes = [CookieJWTAuthentication]

    def create(self, request):
        to_user_id = request.data.get('to_user_id')
        from_user = request.user

        if str(from_user.id) == str(to_user_id):
            return Response({'error': "Вы не можете добавить себя"}, status=400)

        try:
            # Получаем пользователя по ID
            to_user = CustomUser.objects.get(id=to_user_id)
            # Получаем профиль пользователя
            to_user_profile = to_user.profile
        except CustomUser.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=404)

        # Получаем профиль отправителя запроса
        from_user_profile = from_user.profile

        # Проверка на уже отправленный запрос
        existing = FriendRequest.objects.filter(
            from_user=from_user_profile, to_user=to_user_profile, status='pending'
        ).exists()

        if existing:
            return Response({'error': 'Запрос на добавление в друзья уже отправлен'}, status=400)

        # Создаем новый запрос
        FriendRequest.objects.create(from_user=from_user_profile, to_user=to_user_profile)
        return Response({'message': 'OK!'}, status=status.HTTP_201_CREATED)


# Получение исходящих запросов в друзья
class GetFriendRequests(viewsets.ViewSet):
    authentication_classes = [CookieJWTAuthentication]

    def list(self, request):
        user_profile = request.user.profile

        incoming = FriendRequest.objects.filter(to_user=user_profile, status='pending')

        return Response({
            'incoming': FriendRequestSerializer(incoming, many=True, context={'request': request}).data
        })


# Принятие/отклонение запроса в друзья
class PostToFriendRequest(viewsets.ViewSet):
    authentication_classes = [CookieJWTAuthentication]

    def create(self, request, request_id):
        action = request.data.get('action')
        user = request.user
        user_profile = user.profile

        try:
            friend_request = FriendRequest.objects.get(id=request_id, to_user=user_profile)
        except FriendRequest.DoesNotExist:
            return Response({'error': f'Запрос с ID {request_id} для пользователя {user_profile} не найден'}, status=404)

        if action == 'accept':
            friend_request.status = 'accepted'
            friend_request.save()

            Friend.objects.create(
                sender=friend_request.from_user,
                receiver=user_profile
            )

            return Response({'message': 'OK!'})
        elif action == 'reject':
            friend_request.status = 'rejected'
            friend_request.save()
            return Response({'message': 'Запрос на добавление в друзья отклонен'})
        else:
            return Response({'error': 'Invalid action'}, status=400)
