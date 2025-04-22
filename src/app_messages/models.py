from django.db import models
from app_channels.models import Channel
from app_users.models import Profile


class Messages(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='direct_messages')
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.TextField()
    file_url = models.URLField(null=True, blank=True)

    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.name}: {self.content[:20]}"
