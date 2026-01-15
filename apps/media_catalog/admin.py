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

    list_display = ['media_ptr', 'director', 'runtime_minutes', 'tmdb_id']
    search_fields = ['media_ptr__title', 'director']
    readonly_fields = ['media_ptr']


@admin.register(TVSeries)
class TVSeriesAdmin(admin.ModelAdmin):
    """Admin interface for TV Series model."""

    list_display = ['media_ptr', 'number_of_seasons', 'number_of_episodes', 'status']
    list_filter = ['status']
    search_fields = ['media_ptr__title']
    readonly_fields = ['media_ptr']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin interface for Book model."""

    list_display = ['media_ptr', 'isbn', 'publisher', 'page_count']
    search_fields = ['media_ptr__title', 'isbn', 'publisher']
    readonly_fields = ['media_ptr']


@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    """Admin interface for Music model."""

    list_display = ['media_ptr', 'album_type', 'track_count', 'label']
    list_filter = ['album_type']
    search_fields = ['media_ptr__title', 'label']
    readonly_fields = ['media_ptr']


@admin.register(Concert)
class ConcertAdmin(admin.ModelAdmin):
    """Admin interface for Concert model."""

    list_display = ['media_ptr', 'artist', 'venue', 'location', 'event_date']
    search_fields = ['media_ptr__title', 'artist', 'venue']
    readonly_fields = ['media_ptr']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin interface for Document model."""

    list_display = ['media_ptr', 'document_type', 'author']
    list_filter = ['document_type']
    search_fields = ['media_ptr__title', 'author']
    readonly_fields = ['media_ptr']
