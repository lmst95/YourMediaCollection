from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import secrets

User = get_user_model()


class Collection(models.Model):
    """User-created collections"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='collections'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Sharing settings
    is_public = models.BooleanField(
        default=False,
        help_text='Allow anyone with the link to view this collection (read-only)'
    )
    share_token = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        help_text='Unique token for shareable link'
    )
    shared_with = models.ManyToManyField(
        User,
        related_name='shared_collections',
        blank=True,
        help_text='Specific users who can view this collection'
    )

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'name']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['share_token']),
        ]

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def item_count(self):
        return self.items.count()

    def save(self, *args, **kwargs):
        # Generate share token if collection is public and doesn't have one
        if self.is_public and not self.share_token:
            self.share_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def get_share_url(self, request=None):
        """Get the shareable URL for this collection"""
        if not self.is_public or not self.share_token:
            return None
        if request:
            from django.urls import reverse
            return request.build_absolute_uri(
                reverse('collections:shared_view', kwargs={'token': self.share_token})
            )
        return None

    def is_shared_with_user(self, user):
        """Check if collection is shared with a specific user"""
        if user == self.user:
            return True  # Owner always has access
        if self.is_public:
            return True  # Public collections accessible to all
        return self.shared_with.filter(pk=user.pk).exists()


class CollectionItem(models.Model):
    """
    Items in a collection (polymorphic - can be Book or Document)
    Uses GenericForeignKey for flexibility
    """

    STATUS_CHOICES = [
        ('READ', 'Gelesen'),
        ('READING', 'Lese gerade'),
        ('WISHLIST', 'Wunschliste'),
        ('BORROWED_FROM', 'Ausgeliehen von'),
        ('BORROWED_TO', 'Ausgeliehen an'),
    ]

    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name='items'
    )

    # Generic relation to Book or Document
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Status tracking (multiple statuses as tags)
    statuses = models.JSONField(default=list, blank=True)  # List of status codes

    # Borrowing details (optional)
    borrowed_person_name = models.CharField(max_length=255, blank=True)
    borrowed_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)

    # Personal notes (quick note, different from Note model)
    personal_note = models.TextField(blank=True)

    # Timestamps
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-added_at']
        unique_together = ['collection', 'content_type', 'object_id']
        indexes = [
            models.Index(fields=['collection', '-added_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.content_object} in {self.collection.name}"

    def get_item_type(self):
        """Returns 'book' or 'document'"""
        return self.content_type.model

    def get_status_displays(self):
        """Returns list of display names for statuses"""
        status_dict = dict(self.STATUS_CHOICES)
        return [status_dict.get(status, status) for status in self.statuses if status in status_dict]

    def has_status(self, status_code):
        """Check if item has a specific status"""
        return status_code in self.statuses
