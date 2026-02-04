from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin interface for Document model"""

    list_display = [
        'title', 'user', 'file_type',
        'display_file_size', 'created_at'
    ]
    list_filter = ['file_type', 'created_at', 'user']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['file_size', 'file_type', 'created_at', 'updated_at']

    fieldsets = (
        ('Document Information', {
            'fields': ('user', 'title', 'description')
        }),
        ('File', {
            'fields': ('file', 'file_type', 'file_size')
        }),
        ('Metadata', {
            'fields': ('authors', 'categories')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def display_file_size(self, obj):
        """Display human-readable file size"""
        return obj.get_file_size_display()
    display_file_size.short_description = 'Dateigröße'
