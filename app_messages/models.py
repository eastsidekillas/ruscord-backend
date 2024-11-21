from django.db import models
from app_users.models import CustomUser
import uuid

class Message(models.Model):
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='sent_messages', to_field='id'
    )
    recipient = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='received_messages', to_field='id'
    )
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


    def __str__(self):
        return f"From {self.sender} to {self.recipient}: {self.text[:30]}"