from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class Todo(models.Model):
    """Todos with optional links to books/documents"""

    STATUS_CHOICES = [
        ('PLANNED', 'Geplant'),
        ('IN_PROGRESS', 'In Bearbeitung'),
        ('COMPLETED', 'Erledigt'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='todos'
    )

    # Todo details
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PLANNED'
    )

    # Due date (optional)
    due_date = models.DateField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def mark_completed(self):
        from django.utils import timezone
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        self.save()


class TodoItem(models.Model):
    """Links todos to books/documents (many-to-many through table)"""
    todo = models.ForeignKey(
        Todo,
        on_delete=models.CASCADE,
        related_name='linked_items'
    )

    # Generic relation to Book or Document
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Timestamps
    linked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['todo', 'content_type', 'object_id']
        indexes = [
            models.Index(fields=['todo']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.content_object} verknüpft mit {self.todo.title}"
