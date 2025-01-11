import uuid
from django.db import models
from app_users.models import CustomUser


class Channel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="Уникальный ID чата")
    members = models.ManyToManyField(CustomUser, related_name='dm_channels', verbose_name="Участники")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Channel {self.uuid}"
