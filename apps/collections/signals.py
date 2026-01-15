"""
Signals for UserMedia model to sync with Neo4j.
This handles the PostgreSQL → Neo4j sync strategy.
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import UserMedia, CollectionStatus
from core.services import Neo4jService

logger = logging.getLogger(__name__)


# Mapping of Django model status to Neo4j relationship types
STATUS_TO_RELATIONSHIP = {
    CollectionStatus.OWNED: 'OWNS',
    CollectionStatus.WATCHED: 'WATCHED',
    CollectionStatus.READ: 'WATCHED',  # Use WATCHED for read items
    CollectionStatus.LISTENED: 'WATCHED',  # Use WATCHED for listened items
    CollectionStatus.WISHLIST: 'WISHES',
    CollectionStatus.IN_PROGRESS: 'IN_PROGRESS',
    CollectionStatus.BORROWED: 'BORROWED',
    CollectionStatus.LENT: 'LENT',
}


@receiver(post_save, sender=UserMedia)
def sync_usermedia_to_neo4j(sender, instance, created, **kwargs):
    """
    Sync UserMedia to Neo4j when created or updated.
    Creates relationship between User and Media nodes.
    """
    try:
        neo4j = Neo4jService()
        neo4j.connect()

        # Ensure Media node exists
        neo4j.create_media_node(
            media_id=str(instance.media.id),
            media_type=instance.media.media_type,
            title=instance.media.title,
            genres=instance.media.genres
        )

        # Create genres and relationships
        if instance.media.genres:
            neo4j.create_genre_nodes(instance.media.genres)
            for genre in instance.media.genres:
                neo4j.create_genre_relationship(str(instance.media.id), genre)

        # Create collection relationship
        relationship_type = STATUS_TO_RELATIONSHIP.get(instance.status, 'OWNS')
        properties = {
            'added_at': instance.added_at.isoformat() if instance.added_at else None,
            'rating': float(instance.rating) if instance.rating else None,
            'notes': instance.notes or '',
            'completed_at': instance.completed_at.isoformat() if instance.completed_at else None,
        }

        neo4j.create_collection_relationship(
            user_id=str(instance.user.id),
            media_id=str(instance.media.id),
            relationship_type=relationship_type,
            **properties
        )

        neo4j.close()
        logger.info(f"Synced UserMedia to Neo4j: {instance.user.username} -> {instance.media.title}")
    except Exception as e:
        logger.error(f"Failed to sync UserMedia to Neo4j: {e}")


@receiver(post_delete, sender=UserMedia)
def delete_usermedia_from_neo4j(sender, instance, **kwargs):
    """
    Delete UserMedia relationship from Neo4j when collection item is deleted.
    """
    try:
        neo4j = Neo4jService()
        neo4j.connect()

        relationship_type = STATUS_TO_RELATIONSHIP.get(instance.status, 'OWNS')
        neo4j.delete_collection_relationship(
            user_id=str(instance.user.id),
            media_id=str(instance.media.id),
            relationship_type=relationship_type
        )

        neo4j.close()
        logger.info(f"Deleted UserMedia from Neo4j: {instance.user.username} -> {instance.media.title}")
    except Exception as e:
        logger.error(f"Failed to delete UserMedia from Neo4j: {e}")
