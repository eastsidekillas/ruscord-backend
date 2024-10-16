from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


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
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=11, null=True, blank=True)
    avatar_url = models.URLField(null=True, blank=True)
    bio = models.TextField(blank=True, null=True)  # Краткая информация о пользователе

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
        return True  # Ваша логика разрешений

    def has_module_perms(self, app_label):
        """Returns True if the user has permissions for the specified app label."""
        return True  # Ваша логика разрешений

    def get_group_permissions(self, obj=None):
        """Returns a set of permissions for groups the user belongs to."""
        return set()  # Ваша логика разрешений
