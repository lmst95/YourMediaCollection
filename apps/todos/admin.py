from django.contrib import admin
from .models import Todo, TodoItem


class TodoItemInline(admin.TabularInline):
    """Inline display of linked items"""
    model = TodoItem
    extra = 0
    fields = ['content_object', 'linked_at']
    readonly_fields = ['content_object', 'linked_at']


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    """Admin interface for Todo model"""

    list_display = [
        'title', 'user', 'status', 'due_date',
        'created_at', 'completed_at'
    ]
    list_filter = ['status', 'user', 'due_date', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    inlines = [TodoItemInline]

    fieldsets = (
        ('Todo Information', {
            'fields': ('user', 'title', 'description', 'status', 'due_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )

    actions = ['mark_as_completed']

    def mark_as_completed(self, request, queryset):
        """Mark selected todos as completed"""
        for todo in queryset:
            todo.mark_completed()
        self.message_user(request, f'{queryset.count()} Aufgabe(n) als erledigt markiert.')
    mark_as_completed.short_description = 'Markiere als erledigt'


@admin.register(TodoItem)
class TodoItemAdmin(admin.ModelAdmin):
    """Admin interface for TodoItem model"""

    list_display = ['todo', 'content_object', 'linked_at']
    list_filter = ['content_type', 'linked_at']
    search_fields = ['todo__title']
    readonly_fields = ['content_type', 'object_id', 'linked_at']

    fieldsets = (
        ('Todo', {
            'fields': ('todo',)
        }),
        ('Linked Item', {
            'fields': ('content_type', 'object_id')
        }),
        ('Timestamps', {
            'fields': ('linked_at',)
        }),
    )
