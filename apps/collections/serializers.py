"""
Serializers for collections app - REDESIGNED for new model structure.
"""

from rest_framework import serializers
from apps.collections.models import UserMediaCollection, LendingRecord
from apps.media_catalog.serializers import MediaListSerializer


class LendingRecordSerializer(serializers.ModelSerializer):
    """Serializer for lending/borrowing records."""

    class Meta:
        model = LendingRecord
        fields = [
            'id',
            'lending_type',
            'person_name',
            'notes',
            'lent_at',
            'returned_at',
            'is_returned',
        ]
        read_only_fields = ['id', 'lent_at']


class UserMediaCollectionSerializer(serializers.ModelSerializer):
    """Serializer for reading user media collection items."""

    media_details = MediaListSerializer(source='media', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    status_flags = serializers.ListField(read_only=True)
    lending_records = LendingRecordSerializer(many=True, read_only=True)

    # Active lending info
    active_lent_to = serializers.SerializerMethodField()
    active_borrowed_from = serializers.SerializerMethodField()

    class Meta:
        model = UserMediaCollection
        fields = [
            'id',
            'user',
            'user_username',
            'media',
            'media_details',
            'rating',
            'notes',
            'is_owned',
            'is_wishlist',
            'is_watched',
            'is_in_progress',
            'status_flags',
            'added_at',
            'watched_at',
            'updated_at',
            'lending_records',
            'active_lent_to',
            'active_borrowed_from',
        ]
        read_only_fields = ['id', 'user', 'added_at', 'updated_at']

    def get_active_lent_to(self, obj):
        """Get list of people currently borrowing this item."""
        lent = obj.lending_records.filter(lending_type='lent', is_returned=False)
        return [record.person_name for record in lent]

    def get_active_borrowed_from(self, obj):
        """Get list of people this item is currently borrowed from."""
        borrowed = obj.lending_records.filter(lending_type='borrowed', is_returned=False)
        return [record.person_name for record in borrowed]

    def validate_rating(self, value):
        """Validate that rating is between 0 and 10."""
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError("Rating must be between 0.0 and 10.0")
        return value


class UserMediaCollectionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/adding to collection."""

    # Accept status flags as list for easier frontend integration
    statuses = serializers.ListField(
        child=serializers.ChoiceField(choices=['owned', 'wishlist', 'watched', 'in_progress']),
        write_only=True,
        required=False,
        help_text="List of statuses to set (e.g., ['owned', 'wishlist'])"
    )

    # Optional lending info
    lend_to = serializers.CharField(write_only=True, required=False, allow_blank=True)
    borrow_from = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = UserMediaCollection
        fields = [
            'media',
            'rating',
            'notes',
            'is_owned',
            'is_wishlist',
            'is_watched',
            'is_in_progress',
            'watched_at',
            'statuses',  # Alternative to individual flags
            'lend_to',
            'borrow_from',
        ]

    def validate_rating(self, value):
        """Validate that rating is between 0 and 10."""
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError("Rating must be between 0.0 and 10.0")
        return value

    def create(self, validated_data):
        """Create collection item with user and handle statuses list."""
        user = self.context['request'].user

        # Extract special fields
        statuses = validated_data.pop('statuses', [])
        lend_to = validated_data.pop('lend_to', None)
        borrow_from = validated_data.pop('borrow_from', None)

        # Set flags from statuses list if provided
        if statuses:
            validated_data['is_owned'] = 'owned' in statuses
            validated_data['is_wishlist'] = 'wishlist' in statuses
            validated_data['is_watched'] = 'watched' in statuses
            validated_data['is_in_progress'] = 'in_progress' in statuses

        validated_data['user'] = user
        collection_item = super().create(validated_data)

        # Create lending records if specified
        if lend_to:
            LendingRecord.objects.create(
                collection_item=collection_item,
                lending_type='lent',
                person_name=lend_to
            )

        if borrow_from:
            LendingRecord.objects.create(
                collection_item=collection_item,
                lending_type='borrowed',
                person_name=borrow_from
            )

        return collection_item


class UserMediaCollectionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating collection items."""

    statuses = serializers.ListField(
        child=serializers.ChoiceField(choices=['owned', 'wishlist', 'watched', 'in_progress']),
        write_only=True,
        required=False
    )

    class Meta:
        model = UserMediaCollection
        fields = [
            'rating',
            'notes',
            'is_owned',
            'is_wishlist',
            'is_watched',
            'is_in_progress',
            'watched_at',
            'statuses',
        ]

    def validate_rating(self, value):
        """Validate that rating is between 0 and 10."""
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError("Rating must be between 0.0 and 10.0")
        return value

    def update(self, instance, validated_data):
        """Update collection item and handle statuses list."""
        statuses = validated_data.pop('statuses', None)

        if statuses is not None:
            # Update flags based on statuses list
            instance.is_owned = 'owned' in statuses
            instance.is_wishlist = 'wishlist' in statuses
            instance.is_watched = 'watched' in statuses
            instance.is_in_progress = 'in_progress' in statuses

        return super().update(instance, validated_data)


class CollectionStatsSerializer(serializers.Serializer):
    """Serializer for collection statistics."""

    total_items = serializers.IntegerField()
    by_type = serializers.DictField(child=serializers.IntegerField())
    by_flags = serializers.DictField(child=serializers.IntegerField())
    average_rating = serializers.FloatField(allow_null=True)
    total_owned = serializers.IntegerField()
    total_wishlist = serializers.IntegerField()
    total_watched = serializers.IntegerField()
    total_in_progress = serializers.IntegerField()


# Backward compatibility aliases for old views
UserMediaSerializer = UserMediaCollectionSerializer
UserMediaCreateSerializer = UserMediaCollectionCreateSerializer
UserMediaUpdateSerializer = UserMediaCollectionUpdateSerializer
