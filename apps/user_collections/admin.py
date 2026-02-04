from django.contrib import admin
from .models import Collection, CollectionItem


class CollectionItemInline(admin.TabularInline):
    """Inline display of collection items"""
    model = CollectionItem
    extra = 0
    fields = ['content_object', 'statuses', 'borrowed_person_name', 'added_at']
    readonly_fields = ['content_object', 'added_at']


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    """Admin interface for Collection model"""

    list_display = ['name', 'user', 'item_count', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CollectionItemInline]

    fieldsets = (
        ('Collection Information', {
            'fields': ('user', 'name', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    """Admin interface for CollectionItem model"""

    list_display = [
        'collection', 'content_object', 'display_statuses',
        'get_item_type', 'added_at'
    ]
    list_filter = ['content_type', 'added_at']
    search_fields = ['collection__name', 'collection__user__username']
    readonly_fields = ['content_type', 'object_id', 'added_at', 'updated_at']

    fieldsets = (
        ('Collection', {
            'fields': ('collection',)
        }),
        ('Item Reference', {
            'fields': ('content_type', 'object_id')
        }),
        ('Status', {
            'fields': ('statuses', 'personal_note')
        }),
        ('Borrowing Details', {
            'fields': ('borrowed_person_name', 'borrowed_date', 'return_date'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('added_at', 'updated_at')
        }),
    )

    def display_statuses(self, obj):
        """Display statuses as comma-separated list"""
        if obj.statuses:
            return ', '.join(obj.get_status_displays())
        return '-'
    display_statuses.short_description = 'Status'
