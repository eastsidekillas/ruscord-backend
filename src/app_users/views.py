from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from app_auth.base_auth import CookieJWTAuthentication
from app_channels.models import Channel
from app_channels.serializers import ChannelSerializer
from app_friends.models import Friend
from .models import CustomUser, Profile
from .serializers import CustomUserSerializer, ProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class GetUserProfile(APIView):
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request, user_pk):
        profile = get_object_or_404(Profile, user_id=user_pk)
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)


class GetUserChannels(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [CookieJWTAuthentication]
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_pk')
        channels = Channel.objects.filter(participants__user_id=user_id)
        if not channels.exists():
            raise NotFound()
        return channels


class MeProfileView(APIView):
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        if 'name' in request.data:
            profile.name = request.data['name']
        if 'bio' in request.data:
            profile.bio = request.data['bio']
        if 'global_name' in request.data:
            profile.global_name = request.data['global_name']
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        elif request.data.get('remove_avatar') == 'true' and profile.avatar:
            profile.avatar.delete(save=False)
            profile.avatar = None
        profile.save()
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)


class PostUsersSearch(APIView):
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        query = request.query_params.get('name', '').strip()
        if not query:
            return Response([])

        current_profile = request.user.profile

        # Получаем список ID всех друзей (в обе стороны)
        friends = Friend.objects.filter(
            Q(sender=current_profile) | Q(receiver=current_profile)
        )

        friend_ids = set()
        for f in friends:
            if f.sender == current_profile:
                friend_ids.add(f.receiver.id)
            else:
                friend_ids.add(f.sender.id)

        # Поиск по имени, исключая себя и уже добавленных друзей
        profiles = Profile.objects.filter(
            name__icontains=query
        ).exclude(
            Q(id__in=friend_ids) | Q(id=current_profile.id)
        )[:10]

        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)