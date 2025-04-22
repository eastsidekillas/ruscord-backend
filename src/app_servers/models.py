import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta
from app_users.models import Profile


class Server(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='servers/', null=True, blank=True)
    owner = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_servers')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Member(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='memberships')
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='members')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'server')  # чтобы не было дубликатов

    def __str__(self):
        return f"{self.profile.name} in {self.server.name}"


class InviteLink(models.Model):
    token = models.CharField(max_length=64, unique=True, default=uuid.uuid4)
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='invite_links')
    creator = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    max_uses = models.PositiveIntegerField(null=True, blank=True)  # None = unlimited
    uses = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        if self.max_uses is not None and self.uses >= self.max_uses:
            return False
        return True

    def __str__(self):
        return f"Invite to {self.server.name} ({self.token})"
