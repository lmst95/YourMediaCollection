"""
Admin configuration for media_catalog app.
"""

from django.contrib import admin
from .models import Media, Movie, TVSeries, Book, Music, Concert, Document


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    """Admin interface for base Media model."""

    list_display = ['title', 'media_type', 'release_date', 'is_public', 'created_at']
    list_filter = ['media_type', 'is_public', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'media_type', 'title', 'description', 'release_date', 'cover_image_url')
        }),
        ('Metadata', {
            'fields': ('genres', 'external_ids', 'metadata')
        }),
        ('Access Control', {
            'fields': ('is_public', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """Admin interface for Movie model."""

    list_display = ['title', 'director', 'runtime_minutes', 'tmdb_id', 'release_date']
    list_filter = ['release_date']
    search_fields = ['title', 'director']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(TVSeries)
class TVSeriesAdmin(admin.ModelAdmin):
    """Admin interface for TV Series model."""

    list_display = ['title', 'number_of_seasons', 'number_of_episodes', 'status', 'release_date']
    list_filter = ['status', 'release_date']
    search_fields = ['title']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin interface for Book model."""

    list_display = ['title', 'isbn', 'publisher', 'page_count', 'release_date']
    list_filter = ['release_date', 'language']
    search_fields = ['title', 'isbn', 'publisher']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    """Admin interface for Music model."""

    list_display = ['title', 'album_type', 'track_count', 'label', 'release_date']
    list_filter = ['album_type', 'release_date']
    search_fields = ['title', 'label']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Concert)
class ConcertAdmin(admin.ModelAdmin):
    """Admin interface for Concert model."""

    list_display = ['title', 'artist', 'venue', 'location', 'event_date']
    list_filter = ['event_date']
    search_fields = ['title', 'artist', 'venue']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin interface for Document model."""

    list_display = ['title', 'document_type', 'author', 'release_date']
    list_filter = ['document_type', 'release_date']
    search_fields = ['title', 'author']
    readonly_fields = ['id', 'created_at', 'updated_at']
