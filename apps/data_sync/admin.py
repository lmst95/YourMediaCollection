"""
Admin configuration for data_sync app.
"""

from django.contrib import admin
from .models import SyncTask


@admin.register(SyncTask)
class SyncTaskAdmin(admin.ModelAdmin):
    """Admin interface for SyncTask model."""

    list_display = ['source', 'media_type', 'status', 'records_processed', 'last_sync_at', 'created_at']
    list_filter = ['source', 'status', 'created_at']
    search_fields = ['source', 'media_type']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at']

    fieldsets = (
        ('Task Information', {
            'fields': ('id', 'source', 'media_type', 'status')
        }),
        ('Sync Details', {
            'fields': ('records_processed', 'errors', 'last_sync_at', 'next_sync_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
