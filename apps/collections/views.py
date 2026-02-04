"""
Views for collections app - UPDATED for new UserMediaCollection model.
"""

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from apps.collections.models import UserMediaCollection, LendingRecord
from apps.collections.serializers import (
    UserMediaCollectionSerializer,
    UserMediaCollectionCreateSerializer,
    UserMediaCollectionUpdateSerializer,
    CollectionStatsSerializer,
    LendingRecordSerializer,
)


@extend_schema_view(
    get=extend_schema(
        summary="Get my collection",
        description="Retrieve the authenticated user's media collection with all property flags.",
        tags=["Collections"],
        parameters=[
            OpenApiParameter(
                name='flag',
                description='Filter by property flag: owned, wishlist, watched, in_progress',
                required=False,
                type=str
            ),
        ]
    )
)
class MyCollectionView(generics.ListAPIView):
    """
    Get authenticated user's collection.
    GET /api/collections/my/
    """
    serializer_class = UserMediaCollectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return current user's collection with optional flag filter."""
        # Handle swagger fake view
        if getattr(self, 'swagger_fake_view', False):
            return UserMediaCollection.objects.none()

        queryset = UserMediaCollection.objects.filter(
            user=self.request.user
        ).select_related('media', 'user').prefetch_related('lending_records')

        # Filter by flag if provided
        flag = self.request.query_params.get('flag', None)
        if flag == 'owned':
            queryset = queryset.filter(is_owned=True)
        elif flag == 'wishlist':
            queryset = queryset.filter(is_wishlist=True)
        elif flag == 'watched':
            queryset = queryset.filter(is_watched=True)
        elif flag == 'in_progress':
            queryset = queryset.filter(is_in_progress=True)

        return queryset.order_by('-added_at')


@extend_schema_view(
    post=extend_schema(
        summary="Add media to collection",
        description="Add a media item to your collection with multiple property flags.",
        tags=["Collections"],
    )
)
class CollectionCreateView(generics.CreateAPIView):
    """
    Add media to collection.
    POST /api/collections/
    """
    serializer_class = UserMediaCollectionCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Override create to handle unique constraint violations gracefully."""
        from django.db import IntegrityError
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            # Handle unique constraint violation
            return Response(
                {'detail': 'This media already exists in your collection. Use PATCH to update it.'},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema_view(
    get=extend_schema(
        summary="Get collection item details",
        description="Retrieve details of a specific item in your collection.",
        tags=["Collections"],
    ),
    patch=extend_schema(
        summary="Update collection item",
        description="Update property flags, rating, or notes for a collection item.",
        tags=["Collections"],
    ),
    delete=extend_schema(
        summary="Remove from collection",
        description="Remove a media item from your collection completely.",
        tags=["Collections"],
    ),
)
class CollectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a collection item.
    GET/PATCH/DELETE /api/collections/{id}/
    """
    serializer_class = UserMediaCollectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Only allow users to access their own collection items."""
        return UserMediaCollection.objects.filter(user=self.request.user).prefetch_related('lending_records')

    def get_serializer_class(self):
        """Use update serializer for PATCH."""
        if self.request.method == 'PATCH':
            return UserMediaCollectionUpdateSerializer
        return UserMediaCollectionSerializer


@extend_schema(
    summary="Get collection statistics",
    description="Get statistics about your collection (counts by type, flags, average rating).",
    tags=["Collections"],
    responses={200: CollectionStatsSerializer},
)
class CollectionStatsView(APIView):
    """
    Get collection statistics.
    GET /api/collections/stats/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return collection statistics."""
        user = request.user
        collection = UserMediaCollection.objects.filter(user=user)

        # Total items
        total_items = collection.count()

        # By media type
        by_type = {}
        type_counts = collection.values('media__media_type').annotate(count=Count('id'))
        for item in type_counts:
            by_type[item['media__media_type']] = item['count']

        # By flags
        by_flags = {
            'owned': collection.filter(is_owned=True).count(),
            'wishlist': collection.filter(is_wishlist=True).count(),
            'watched': collection.filter(is_watched=True).count(),
            'in_progress': collection.filter(is_in_progress=True).count(),
        }

        # Average rating
        avg_rating = collection.aggregate(avg=Avg('rating'))['avg']

        stats = {
            'total_items': total_items,
            'by_type': by_type,
            'by_flags': by_flags,
            'average_rating': round(avg_rating, 2) if avg_rating else None,
            'total_owned': by_flags['owned'],
            'total_wishlist': by_flags['wishlist'],
            'total_watched': by_flags['watched'],
            'total_in_progress': by_flags['in_progress'],
        }

        serializer = CollectionStatsSerializer(stats)
        return Response(serializer.data)


@extend_schema(
    summary="Get collection timeline",
    description="Get a timeline of collection activities (recently added items).",
    tags=["Collections"],
)
class CollectionTimelineView(generics.ListAPIView):
    """
    Get collection activity timeline.
    GET /api/collections/timeline/
    """
    serializer_class = UserMediaCollectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return recent collection activities."""
        # Handle swagger fake view
        if getattr(self, 'swagger_fake_view', False):
            return UserMediaCollection.objects.none()

        return UserMediaCollection.objects.filter(
            user=self.request.user
        ).select_related('media', 'user').prefetch_related('lending_records').order_by('-added_at')[:50]


@extend_schema_view(
    get=extend_schema(
        summary="Get lending records",
        description="Get all lending/borrowing records for a collection item.",
        tags=["Collections"],
    ),
    post=extend_schema(
        summary="Add lending record",
        description="Record that you lent or borrowed this item.",
        tags=["Collections"],
    ),
)
class LendingRecordListView(generics.ListCreateAPIView):
    """
    List and create lending records.
    GET/POST /api/collections/{collection_id}/lending/
    """
    serializer_class = LendingRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return lending records for the collection item."""
        collection_id = self.kwargs.get('collection_id')
        return LendingRecord.objects.filter(
            collection_item_id=collection_id,
            collection_item__user=self.request.user
        ).order_by('-lent_at')

    def perform_create(self, serializer):
        """Associate the lending record with the collection item."""
        collection_id = self.kwargs.get('collection_id')
        collection_item = UserMediaCollection.objects.get(
            id=collection_id,
            user=self.request.user
        )
        serializer.save(collection_item=collection_item)


@extend_schema_view(
    patch=extend_schema(
        summary="Mark lending record as returned",
        description="Update a lending record to mark the item as returned.",
        tags=["Collections"],
    ),
    delete=extend_schema(
        summary="Delete lending record",
        description="Delete a lending/borrowing record.",
        tags=["Collections"],
    ),
)
class LendingRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a lending record.
    GET/PATCH/DELETE /api/collections/lending/{id}/
    """
    serializer_class = LendingRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Only allow users to access their own lending records."""
        return LendingRecord.objects.filter(collection_item__user=self.request.user)
