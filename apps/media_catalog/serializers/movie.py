"""
Movie serializer.
"""

from rest_framework import serializers
from apps.media_catalog.models import Movie, Media, MediaType


class MovieSerializer(serializers.ModelSerializer):
    """Serializer for Movie model."""

    # Include base Media fields
    title = serializers.CharField(source='media_ptr.title')
    description = serializers.CharField(source='media_ptr.description', required=False, allow_blank=True)
    release_date = serializers.DateField(source='media_ptr.release_date', required=False, allow_null=True)
    cover_image_url = serializers.URLField(source='media_ptr.cover_image_url', required=False, allow_blank=True)
    genres = serializers.JSONField(source='media_ptr.genres', required=False)
    external_ids = serializers.JSONField(source='media_ptr.external_ids', required=False)

    class Meta:
        model = Movie
        fields = [
            'media_ptr',
            'title',
            'description',
            'release_date',
            'cover_image_url',
            'genres',
            'external_ids',
            'runtime_minutes',
            'director',
            'cast',
            'tmdb_id',
            'imdb_id',
        ]
        read_only_fields = ['media_ptr']

    def create(self, validated_data):
        """Create Movie with associated Media instance."""
        media_data = validated_data.pop('media_ptr', {})
        media_data['media_type'] = MediaType.MOVIE

        # Create the base Media instance
        media = Media.objects.create(**media_data)

        # Create the Movie instance
        movie = Movie.objects.create(media_ptr=media, **validated_data)

        return movie
