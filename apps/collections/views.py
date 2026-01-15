"""
Views for collections app.
"""

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from apps.collections.models import UserMedia, CollectionStatus
from apps.collections.serializers import (
    UserMediaSerializer,
    UserMediaCreateSerializer,
    UserMediaUpdateSerializer,
    CollectionStatsSerializer,
)


@extend_schema_view(
    get=extend_schema(
        summary="Get my collection",
        description="Retrieve the authenticated user's media collection.",
        tags=["Collections"],
        parameters=[
            OpenApiParameter(
                name='status',
                description='Filter by collection status',
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
    serializer_class = UserMediaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return current user's collection with optional status filter."""
        queryset = UserMedia.objects.filter(user=self.request.user).select_related('media', 'user')

        # Filter by status if provided
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset.order_by('-added_at')


@extend_schema_view(
    post=extend_schema(
        summary="Add media to collection",
        description="Add a media item to your collection with a status.",
        tags=["Collections"],
    )
)
class CollectionCreateView(generics.CreateAPIView):
    """
    Add media to collection.
    POST /api/collections/
    """
    serializer_class = UserMediaCreateSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    get=extend_schema(
        summary="Get collection item details",
        description="Retrieve details of a specific item in your collection.",
        tags=["Collections"],
    ),
    patch=extend_schema(
        summary="Update collection item",
        description="Update status, rating, or notes for a collection item.",
        tags=["Collections"],
    ),
    delete=extend_schema(
        summary="Remove from collection",
        description="Remove a media item from your collection.",
        tags=["Collections"],
    ),
)
class CollectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a collection item.
    GET/PATCH/DELETE /api/collections/{id}/
    """
    serializer_class = UserMediaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Only allow users to access their own collection items."""
        return UserMedia.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Use update serializer for PATCH."""
        if self.request.method == 'PATCH':
            return UserMediaUpdateSerializer
        return UserMediaSerializer


@extend_schema(
    summary="Get collection statistics",
    description="Get statistics about your collection (counts by type, status, average rating).",
    tags=["Collections"],
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
        collection = UserMedia.objects.filter(user=user)

        # Total items
        total_items = collection.count()

        # By media type
        by_type = {}
        type_counts = collection.values('media__media_type').annotate(count=Count('id'))
        for item in type_counts:
            by_type[item['media__media_type']] = item['count']

        # By status
        by_status = {}
        status_counts = collection.values('status').annotate(count=Count('id'))
        for item in status_counts:
            by_status[item['status']] = item['count']

        # Average rating
        avg_rating = collection.aggregate(avg=Avg('rating'))['avg']

        stats = {
            'total_items': total_items,
            'by_type': by_type,
            'by_status': by_status,
            'average_rating': round(avg_rating, 2) if avg_rating else None,
        }

        serializer = CollectionStatsSerializer(stats)
        return Response(serializer.data)


@extend_schema(
    summary="Get collection timeline",
    description="Get a timeline of collection activities (recently added, completed).",
    tags=["Collections"],
)
class CollectionTimelineView(generics.ListAPIView):
    """
    Get collection activity timeline.
    GET /api/collections/timeline/
    """
    serializer_class = UserMediaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return recent collection activities."""
        return UserMedia.objects.filter(
            user=self.request.user
        ).select_related('media', 'user').order_by('-added_at')[:50]
