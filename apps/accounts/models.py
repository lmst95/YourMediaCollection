from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended user model for YourMediaCollection2"""

    # Profile information
    bio = models.TextField(blank=True, max_length=500)
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )

    # Preferences
    # TODO: Add default_collection after user_collections.Collection is created
    # default_collection = models.ForeignKey(
    #     'user_collections.Collection',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name='default_for_users'
    # )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
