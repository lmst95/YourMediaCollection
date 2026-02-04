from django.contrib import admin
from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    """Admin interface for Activity model"""

    list_display = [
        'user', 'activity_type', 'display_description',
        'content_object', 'created_at'
    ]
    list_filter = ['activity_type', 'user', 'created_at']
    search_fields = ['description', 'user__username']
    readonly_fields = ['content_type', 'object_id', 'created_at']

    fieldsets = (
        ('Activity Information', {
            'fields': ('user', 'activity_type', 'description')
        }),
        ('Related Object', {
            'fields': ('content_type', 'object_id')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )

    def display_description(self, obj):
        """Truncate long descriptions"""
        return obj.description[:75] + '...' if len(obj.description) > 75 else obj.description
    display_description.short_description = 'Beschreibung'
