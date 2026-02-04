from django.contrib import admin
from .models import Book, BookRating, BookReadStatus


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin interface for Book model"""

    list_display = [
        'title', 'publication_year', 'display_authors',
        'average_rating', 'rating_count', 'created_at'
    ]
    list_filter = ['publication_year', 'language', 'created_at']
    search_fields = ['title', 'subtitle', 'dnb_id', 'isbn']
    readonly_fields = [
        'dnb_id', 'average_rating', 'rating_count',
        'created_at', 'updated_at', 'dnb_raw_data'
    ]

    fieldsets = (
        ('DNB Identifiers', {
            'fields': ('dnb_id', 'isbn')
        }),
        ('Basic Information', {
            'fields': ('title', 'subtitle', 'authors', 'publishers', 'publication_year', 'language')
        }),
        ('Additional Metadata', {
            'fields': ('categories', 'description', 'page_count')
        }),
        ('Ratings', {
            'fields': ('average_rating', 'rating_count')
        }),
        ('Raw Data', {
            'fields': ('dnb_raw_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def display_authors(self, obj):
        """Display authors as comma-separated list"""
        return ', '.join(obj.authors) if obj.authors else '-'
    display_authors.short_description = 'Autoren'


@admin.register(BookRating)
class BookRatingAdmin(admin.ModelAdmin):
    """Admin interface for BookRating model"""

    list_display = ['user', 'book', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'book__title']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Rating Information', {
            'fields': ('user', 'book', 'rating', 'review_text')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(BookReadStatus)
class BookReadStatusAdmin(admin.ModelAdmin):
    """Admin interface for BookReadStatus model"""

    list_display = ['user', 'book', 'is_read', 'read_date', 'created_at']
    list_filter = ['is_read', 'read_date', 'created_at']
    search_fields = ['user__username', 'book__title']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Read Status Information', {
            'fields': ('user', 'book', 'is_read', 'read_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
