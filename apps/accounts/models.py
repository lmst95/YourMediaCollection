"""
User models for the accounts app.
"""

import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""

    def create_user(self, username, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        if not username:
            raise ValueError(_('The Username field must be set'))

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model with UUID primary key and additional fields."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    avatar_url = models.URLField(_('avatar URL'), max_length=500, blank=True)
    bio = models.TextField(_('biography'), blank=True)
    preferences = models.JSONField(_('user preferences'), default=dict, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'accounts_user'
        verbose_name = _('user')
        verbose_name_plural = _('users')
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.username

    def get_full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.username
