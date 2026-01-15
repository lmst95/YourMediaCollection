"""
Serializers for collections app.
"""

from rest_framework import serializers
from apps.collections.models import UserMedia, CollectionStatus
from apps.media_catalog.serializers import MediaListSerializer


class UserMediaSerializer(serializers.ModelSerializer):
    """Serializer for UserMedia model."""

    media_details = MediaListSerializer(source='media', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserMedia
        fields = [
            'id',
            'user',
            'user_username',
            'media',
            'media_details',
            'status',
            'status_display',
            'rating',
            'notes',
            'added_at',
            'completed_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'added_at', 'updated_at']

    def validate_rating(self, value):
        """Validate that rating is between 0 and 10."""
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError("Rating must be between 0.0 and 10.0")
        return value


class UserMediaCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating UserMedia (adding to collection)."""

    class Meta:
        model = UserMedia
        fields = [
            'media',
            'status',
            'rating',
            'notes',
            'completed_at',
        ]

    def validate_rating(self, value):
        """Validate that rating is between 0 and 10."""
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError("Rating must be between 0.0 and 10.0")
        return value

    def create(self, validated_data):
        """Create UserMedia with authenticated user."""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class UserMediaUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating UserMedia."""

    class Meta:
        model = UserMedia
        fields = [
            'status',
            'rating',
            'notes',
            'completed_at',
        ]

    def validate_rating(self, value):
        """Validate that rating is between 0 and 10."""
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError("Rating must be between 0.0 and 10.0")
        return value


class CollectionStatsSerializer(serializers.Serializer):
    """Serializer for collection statistics."""

    total_items = serializers.IntegerField()
    by_type = serializers.DictField(child=serializers.IntegerField())
    by_status = serializers.DictField(child=serializers.IntegerField())
    average_rating = serializers.FloatField(allow_null=True)
