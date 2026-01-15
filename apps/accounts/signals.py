"""
Signals for User model to sync with Neo4j.
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import User
from core.services import Neo4jService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def sync_user_to_neo4j(sender, instance, created, **kwargs):
    """
    Sync User to Neo4j when created or updated.
    """
    try:
        neo4j = Neo4jService()
        neo4j.connect()
        neo4j.create_user_node(
            user_id=str(instance.id),
            username=instance.username,
            created_at=instance.created_at.isoformat() if instance.created_at else None
        )
        neo4j.close()
        logger.info(f"Synced User to Neo4j: {instance.username}")
    except Exception as e:
        logger.error(f"Failed to sync User to Neo4j: {e}")


@receiver(post_delete, sender=User)
def delete_user_from_neo4j(sender, instance, **kwargs):
    """
    Delete User node from Neo4j when user is deleted.
    """
    try:
        neo4j = Neo4jService()
        neo4j.connect()
        neo4j.delete_node('User', str(instance.id))
        neo4j.close()
        logger.info(f"Deleted User from Neo4j: {instance.username}")
    except Exception as e:
        logger.error(f"Failed to delete User from Neo4j: {e}")
