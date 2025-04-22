from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import GetUserFriends, GetFriendRequests, PostFriendRequest, PostToFriendRequest

router = SimpleRouter()
router.register(r'users/me/relationships', GetUserFriends, basename='user-relationships')
router.register(r'users/me/friends/requests', GetFriendRequests, basename='user-friend-requests')
router.register(r'users/me/friends/send', PostFriendRequest, basename='user-send-friend-request')
router.register(r'users/me/friends/(?P<request_id>\d+)/respond', PostToFriendRequest, basename='user-respond-to-friend-request')


urlpatterns = [
    path('', include(router.urls)),
]
