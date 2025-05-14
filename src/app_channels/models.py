from django.db import models
from app_users.models import Profile
from app_servers.models import Server


class Channel(models.Model):
    TEXT = 'TEXT'
    AUDIO = 'AUDIO'

    CHANNEL_TYPES = [
        (TEXT, 'Text'),
        (AUDIO, 'Audio'),
    ]

    DM = 'DM'
    GROUP = 'GROUP'

    CHANNEL_SCOPE = [
        (DM, 'Direct Message'),
        (GROUP, 'Group Call'),
    ]

    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='channels', null=True, blank=True)
    name = models.CharField(max_length=255)
    channel_type = models.CharField(max_length=5, choices=CHANNEL_TYPES, default=TEXT)
    scope = models.CharField(max_length=5, choices=CHANNEL_SCOPE, default=DM)

    owner = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_channels')
    participants = models.ManyToManyField(Profile, related_name='channels')

    is_private = models.BooleanField(default=True)
    is_active_call = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.scope})"

    class Meta:
        unique_together = ('server', 'channel_type', 'name')