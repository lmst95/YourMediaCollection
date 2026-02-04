from django.contrib import admin
from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """Admin interface for Note model"""

    list_display = [
        'display_title', 'user', 'content_object',
        'page_number', 'created_at'
    ]
    list_filter = ['user', 'content_type', 'is_public', 'created_at']
    search_fields = ['title', 'content', 'user__username']
    readonly_fields = ['content_type', 'object_id', 'created_at', 'updated_at']

    fieldsets = (
        ('Note Information', {
            'fields': ('user', 'title', 'content', 'page_number')
        }),
        ('Attached To', {
            'fields': ('content_type', 'object_id')
        }),
        ('Settings', {
            'fields': ('is_public',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def display_title(self, obj):
        """Display title or truncated content"""
        if obj.title:
            return obj.title
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    display_title.short_description = 'Titel/Inhalt'
