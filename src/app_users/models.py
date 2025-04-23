import os
from django.db import models
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from ruscord.storage import OverwriteStorage
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True, verbose_name=('Имя пользователя'))
    email = models.EmailField(unique=True, verbose_name=('Email'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=('Дата регистрации'))

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.username


class Profile(models.Model):
    STATUS_CHOICES = [
        ('online', 'В сети'),
        ('busy', 'Занят'),
        ('idle', 'Не активен'),
        ('offline', 'Не в сети'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='offline')
    avatar = models.ImageField(upload_to='avatars/users/', storage=OverwriteStorage, null=True, blank=True)
    global_name = models.CharField(max_length=255, null=True)
    bio = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Проверяем, был ли изменен файл аватара
        if self.avatar and self.avatar.file:
            # Проверяем, не является ли файл уже WebP
            if not self.avatar.name.lower().endswith('.webp'):
                self.avatar = self.convert_image_to_webp(self.avatar, 'avatars/users/')
        super().save(*args, **kwargs)

    def convert_image_to_webp(self, image_field, upload_path):
        img = Image.open(image_field)
        img = img.convert('RGB')
        img.thumbnail((512, 512))

        buffer = BytesIO()
        img.save(buffer, format='WEBP', quality=80)

        name, ext = os.path.splitext(image_field.name)
        webp_name = f"{name}.webp"

        self.avatar.name = webp_name
        return ContentFile(buffer.getvalue(), name=webp_name)
