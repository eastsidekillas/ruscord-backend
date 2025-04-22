from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from app_auth.views import RegistrationAPIView, LoginAPIView, CheckAuthAPIView
from .views import UserViewSet, GetUserProfile, GetUserChannels, PostUsersSearch


router = DefaultRouter()
router.register('users', UserViewSet)

users_router = routers.NestedDefaultRouter(router, r'users', lookup='user')
users_router.register(r'channels', GetUserChannels, basename='user-channels')

urlpatterns = [
    path('users/search/', PostUsersSearch.as_view(), name='user-search'),
    path("users/<int:user_pk>/profile/", GetUserProfile.as_view(), name="user-profile"),
    path('', include(router.urls)),
    path('', include(users_router.urls)),
]

