from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import GetUserFriends, GetFriendRequests, PostFriendRequest, PostToFriendRequest

router = SimpleRouter()
router.register(r'users/me/relationships', GetUserFriends, basename='user-relationships')
router.register(r'users/me/friends/requests', GetFriendRequests, basename='user-friend-requests')
router.register(r'users/me/friends/send', PostFriendRequest, basename='user-send-friend-request')
UUID_RE = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
router.register(rf'users/me/friends/(?P<request_id>{UUID_RE})/respond', PostToFriendRequest, basename='user-respond-to-friend-request')


urlpatterns = [
    path('', include(router.urls)),
]
