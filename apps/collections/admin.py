"""
Admin configuration for collections app.
"""

from django.contrib import admin
from .models import UserMedia


@admin.register(UserMedia)
class UserMediaAdmin(admin.ModelAdmin):
    """Admin interface for UserMedia model."""

    list_display = ['user', 'media', 'status', 'rating', 'added_at']
    list_filter = ['status', 'added_at']
    search_fields = ['user__username', 'media__title']
    ordering = ['-added_at']
    readonly_fields = ['id', 'added_at', 'updated_at']

    fieldsets = (
        ('Relationship', {
            'fields': ('id', 'user', 'media', 'status')
        }),
        ('Personal Data', {
            'fields': ('rating', 'notes')
        }),
        ('Timestamps', {
            'fields': ('added_at', 'completed_at', 'updated_at')
        }),
    )
