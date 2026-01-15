"""
Base serializer for Media models.
"""

from rest_framework import serializers
from apps.media_catalog.models import Media, MediaType


class MediaSerializer(serializers.ModelSerializer):
    """Base serializer for Media model."""

    media_type_display = serializers.CharField(source='get_media_type_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)

    class Meta:
        model = Media
        fields = [
            'id',
            'media_type',
            'media_type_display',
            'title',
            'description',
            'release_date',
            'cover_image_url',
            'genres',
            'external_ids',
            'metadata',
            'is_public',
            'created_by',
            'created_by_username',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """
        Include type-specific fields in representation.
        Gets the specific model (Movie, Book, etc.) and adds its fields.
        """
        representation = super().to_representation(instance)

        # Get the specific media instance
        specific_media = instance.get_specific()

        # Add type-specific fields based on media_type
        if instance.media_type == MediaType.MOVIE and hasattr(specific_media, 'runtime_minutes'):
            representation['runtime_minutes'] = specific_media.runtime_minutes
            representation['director'] = specific_media.director
            representation['cast'] = specific_media.cast
            representation['tmdb_id'] = specific_media.tmdb_id
            representation['imdb_id'] = specific_media.imdb_id

        elif instance.media_type == MediaType.TV_SERIES and hasattr(specific_media, 'number_of_seasons'):
            representation['number_of_seasons'] = specific_media.number_of_seasons
            representation['number_of_episodes'] = specific_media.number_of_episodes
            representation['status'] = specific_media.status
            representation['creators'] = specific_media.creators
            representation['tmdb_id'] = specific_media.tmdb_id

        elif instance.media_type == MediaType.BOOK and hasattr(specific_media, 'authors'):
            representation['authors'] = specific_media.authors
            representation['isbn'] = specific_media.isbn
            representation['publisher'] = specific_media.publisher
            representation['page_count'] = specific_media.page_count
            representation['language'] = specific_media.language
            representation['openlibrary_id'] = specific_media.openlibrary_id

        elif instance.media_type == MediaType.MUSIC and hasattr(specific_media, 'artists'):
            representation['artists'] = specific_media.artists
            representation['album_type'] = specific_media.album_type
            representation['track_count'] = specific_media.track_count
            representation['duration_seconds'] = specific_media.duration_seconds
            representation['label'] = specific_media.label
            representation['musicbrainz_id'] = str(specific_media.musicbrainz_id) if specific_media.musicbrainz_id else None

        elif instance.media_type == MediaType.CONCERT and hasattr(specific_media, 'artist'):
            representation['artist'] = specific_media.artist
            representation['venue'] = specific_media.venue
            representation['location'] = specific_media.location
            representation['event_date'] = specific_media.event_date

        elif instance.media_type == MediaType.DOCUMENT and hasattr(specific_media, 'document_type'):
            representation['document_type'] = specific_media.document_type
            representation['author'] = specific_media.author
            representation['file_url'] = specific_media.file_url

        return representation


class MediaListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for media lists (without all details)."""

    media_type_display = serializers.CharField(source='get_media_type_display', read_only=True)

    class Meta:
        model = Media
        fields = [
            'id',
            'media_type',
            'media_type_display',
            'title',
            'release_date',
            'cover_image_url',
            'genres',
        ]
