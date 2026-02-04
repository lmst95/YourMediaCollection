"""
Signals for UserMediaCollection model to sync with Neo4j.
UPDATED for new collection model structure.
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import UserMediaCollection, LendingRecord
from core.services import Neo4jService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=UserMediaCollection)
def sync_collection_to_neo4j(sender, instance, created, **kwargs):
    """
    Sync UserMediaCollection to Neo4j when created or updated.
    Creates multiple relationships based on active flags.
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

        # Common properties for all relationships
        properties = {
            'added_at': instance.added_at.isoformat() if instance.added_at else None,
            'rating': float(instance.rating) if instance.rating else None,
            'notes': instance.notes or '',
            'watched_at': instance.watched_at.isoformat() if instance.watched_at else None,
        }

        # Create relationships based on active flags
        user_id = str(instance.user.id)
        media_id = str(instance.media.id)

        if instance.is_owned:
            neo4j.create_collection_relationship(
                user_id=user_id,
                media_id=media_id,
                relationship_type='OWNS',
                **properties
            )

        if instance.is_wishlist:
            neo4j.create_collection_relationship(
                user_id=user_id,
                media_id=media_id,
                relationship_type='WISHES',
                **properties
            )

        if instance.is_watched:
            neo4j.create_collection_relationship(
                user_id=user_id,
                media_id=media_id,
                relationship_type='WATCHED',
                **properties
            )

        if instance.is_in_progress:
            neo4j.create_collection_relationship(
                user_id=user_id,
                media_id=media_id,
                relationship_type='IN_PROGRESS',
                **properties
            )

        neo4j.close()
        logger.info(f"Synced collection to Neo4j: {instance.user.username} -> {instance.media.title}")
    except Exception as e:
        logger.error(f"Failed to sync collection to Neo4j: {e}")


@receiver(post_delete, sender=UserMediaCollection)
def delete_collection_from_neo4j(sender, instance, **kwargs):
    """
    Delete all UserMediaCollection relationships from Neo4j when collection item is deleted.
    """
    try:
        neo4j = Neo4jService()
        neo4j.connect()

        user_id = str(instance.user.id)
        media_id = str(instance.media.id)

        # Delete all relationship types
        for rel_type in ['OWNS', 'WISHES', 'WATCHED', 'IN_PROGRESS']:
            try:
                neo4j.delete_collection_relationship(
                    user_id=user_id,
                    media_id=media_id,
                    relationship_type=rel_type
                )
            except Exception as e:
                logger.debug(f"No {rel_type} relationship to delete: {e}")

        neo4j.close()
        logger.info(f"Deleted collection from Neo4j: {instance.user.username} -> {instance.media.title}")
    except Exception as e:
        logger.error(f"Failed to delete collection from Neo4j: {e}")


@receiver(post_save, sender=LendingRecord)
def sync_lending_to_neo4j(sender, instance, created, **kwargs):
    """
    Sync lending record to Neo4j.
    Creates LENT or BORROWED relationships.
    """
    try:
        neo4j = Neo4jService()
        neo4j.connect()

        properties = {
            'person_name': instance.person_name,
            'lent_at': instance.lent_at.isoformat() if instance.lent_at else None,
            'returned_at': instance.returned_at.isoformat() if instance.returned_at else None,
            'is_returned': instance.is_returned,
            'notes': instance.notes or '',
        }

        rel_type = 'LENT' if instance.lending_type == 'lent' else 'BORROWED'

        neo4j.create_collection_relationship(
            user_id=str(instance.collection_item.user.id),
            media_id=str(instance.collection_item.media.id),
            relationship_type=rel_type,
            **properties
        )

        neo4j.close()
        logger.info(f"Synced lending record to Neo4j: {rel_type}")
    except Exception as e:
        logger.error(f"Failed to sync lending record to Neo4j: {e}")
