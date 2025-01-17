from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FriendViewSet

router = DefaultRouter()
router.register(r'friends', FriendViewSet, basename='friends')

urlpatterns = [
    path('', include(router.urls)),
    path('friends/<uuid:pk>/accept_request/<uuid:request_id>/', FriendViewSet.as_view({'post': 'accept_request'}),
         name='friends-accept-request'),

]

