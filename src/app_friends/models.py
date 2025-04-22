from django.db import models
from app_users.models import Profile, CustomUser


# Модель для хранения друзей
class Friend(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_friends')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_friends')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.name} -> {self.receiver.name}"


# Модель для обработки заявок в друзья
class FriendRequest(models.Model):
    from_user = models.ForeignKey(Profile, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(Profile, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.status})"

