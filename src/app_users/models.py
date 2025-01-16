from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
import uuid


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


# Модель пользователя
class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255, unique=True, verbose_name=('Имя пользователя'))
    email = models.EmailField(unique=True, verbose_name=('Email'))
    phone = models.CharField(max_length=11, null=True, blank=True, verbose_name=('Номер телефона'))
    avatar = models.ImageField(upload_to='avatars/users/', null=True, blank=True, verbose_name=('Аватар'))
    bio = models.TextField(blank=True, null=True, verbose_name=('Обо мне'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=('Дата регистрации'))

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        """Returns True if the user has the specified permission."""
        return True

    def has_module_perms(self, app_label):
        """Returns True if the user has permissions for the specified app label."""
        return True

    def get_group_permissions(self, obj=None):
        """Returns a set of permissions for groups the user belongs to."""
        return set()
