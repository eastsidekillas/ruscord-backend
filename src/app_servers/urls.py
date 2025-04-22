from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServerViewSet, ServerInviteJoinView, ServerInviteCreateView, ServerInviteDetailsView


router = DefaultRouter()
router.register(r'servers', ServerViewSet, basename='server')


urlpatterns = [
    path('', include(router.urls)),
    path('servers/invite/<int:pk>/', ServerInviteCreateView.as_view()),
    path('invite/<str:token>/', ServerInviteDetailsView.as_view(), name='invite-details'),
    path('invite/<str:token>/join', ServerInviteJoinView.as_view(), name='join-by-invite'),

] + router.urls
