from django.db import models
from app_users.models import CustomUser


# Модель личных сообщений
class DirectMessage(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_direct_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_direct_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"DM from {self.sender.username} to {self.receiver.username}"


# Модель системы друзей
class Friendship(models.Model):
    requester = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='friend_requests_sent')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='friend_requests_received')
    status = models.CharField(max_length=20, choices=(('pending', 'Pending'), ('accepted', 'Accepted'), ('denied', 'Denied')))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.requester.username} -> {self.receiver.username} ({self.status})"
