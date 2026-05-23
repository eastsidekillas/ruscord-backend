import uuid
from django.db import models
from app_channels.models import Channel
from app_users.models import Profile


class Messages(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='direct_messages')
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.TextField()
    file_url = models.URLField(null=True, blank=True)

    reply_to = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='replies'
    )
    forwarded_from = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='forwards'
    )
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.name}: {self.content[:20]}"
