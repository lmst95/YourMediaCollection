"""
Neo4j Service Layer - abstraction for all Neo4j operations.
This is CRITICAL FILE #4 from the architecture plan.
"""

import logging
from typing import Dict, List, Optional, Any
from neo4j import GraphDatabase, Session
from neo4j.exceptions import Neo4jError
from django.conf import settings

logger = logging.getLogger(__name__)


class Neo4jService:
    """
    Service class for Neo4j graph database operations.
    Provides methods for creating nodes, relationships, and running queries.
    """

    def __init__(self):
        """Initialize Neo4j driver with settings from Django config."""
        self.uri = settings.NEO4J_CONFIG['URI']
        self.user = settings.NEO4J_CONFIG['USER']
        self.password = settings.NEO4J_CONFIG['PASSWORD']
        self.driver = None

    def __enter__(self):
        """Context manager entry - connect to Neo4j."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.close()

    def connect(self):
        """Establish connection to Neo4j."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            logger.info(f"Connected to Neo4j at {self.uri}")
        except Neo4jError as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def verify_connection(self) -> bool:
        """Verify the Neo4j connection is working."""
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS test")
                return result.single()["test"] == 1
        except Neo4jError as e:
            logger.error(f"Connection verification failed: {e}")
            return False

    # ==================== NODE OPERATIONS ====================

    def create_user_node(self, user_id: str, username: str, **properties) -> bool:
        """
        Create or update a User node in Neo4j.

        Args:
            user_id: UUID of the user
            username: Username
            **properties: Additional properties (e.g., created_at)

        Returns:
            bool: Success status
        """
        query = """
        MERGE (u:User {id: $user_id})
        SET u.username = $username,
            u += $properties
        RETURN u
        """
        try:
            with self.driver.session() as session:
                session.run(query, user_id=str(user_id), username=username, properties=properties)
            logger.info(f"Created/updated User node: {username}")
            return True
        except Neo4jError as e:
            logger.error(f"Failed to create User node: {e}")
            return False

    def create_media_node(
        self,
        media_id: str,
        media_type: str,
        title: str,
        genres: List[str] = None,
        **properties
    ) -> bool:
        """
        Create or update a Media node in Neo4j.

        Args:
            media_id: UUID of the media
            media_type: Type of media (movie, book, etc.)
            title: Media title
            genres: List of genre names
            **properties: Additional properties

        Returns:
            bool: Success status
        """
        query = """
        MERGE (m:Media {id: $media_id})
        SET m.media_type = $media_type,
            m.title = $title,
            m.genres = $genres,
            m += $properties
        RETURN m
        """
        try:
            with self.driver.session() as session:
                session.run(
                    query,
                    media_id=str(media_id),
                    media_type=media_type,
                    title=title,
                    genres=genres or [],
                    properties=properties
                )
            logger.info(f"Created/updated Media node: {title}")
            return True
        except Neo4jError as e:
            logger.error(f"Failed to create Media node: {e}")
            return False

    def create_genre_nodes(self, genres: List[str]) -> bool:
        """
        Create Genre nodes if they don't exist.

        Args:
            genres: List of genre names

        Returns:
            bool: Success status
        """
        query = """
        UNWIND $genres AS genre_name
        MERGE (g:Genre {name: genre_name})
        RETURN g
        """
        try:
            with self.driver.session() as session:
                session.run(query, genres=genres)
            logger.info(f"Created/updated {len(genres)} Genre nodes")
            return True
        except Neo4jError as e:
            logger.error(f"Failed to create Genre nodes: {e}")
            return False

    def delete_node(self, node_label: str, node_id: str) -> bool:
        """
        Delete a node by label and ID.

        Args:
            node_label: Node label (User, Media, Genre)
            node_id: Node ID

        Returns:
            bool: Success status
        """
        query = f"""
        MATCH (n:{node_label} {{id: $node_id}})
        DETACH DELETE n
        """
        try:
            with self.driver.session() as session:
                session.run(query, node_id=str(node_id))
            logger.info(f"Deleted {node_label} node: {node_id}")
            return True
        except Neo4jError as e:
            logger.error(f"Failed to delete node: {e}")
            return False

    # ==================== RELATIONSHIP OPERATIONS ====================

    def create_collection_relationship(
        self,
        user_id: str,
        media_id: str,
        relationship_type: str,
        **properties
    ) -> bool:
        """
        Create a relationship between User and Media (OWNS, WATCHED, WISHES, etc.).

        Args:
            user_id: User UUID
            media_id: Media UUID
            relationship_type: Type of relationship (OWNS, WATCHED, WISHES, IN_PROGRESS)
            **properties: Relationship properties (added_at, rating, notes, etc.)

        Returns:
            bool: Success status
        """
        query = f"""
        MATCH (u:User {{id: $user_id}})
        MATCH (m:Media {{id: $media_id}})
        MERGE (u)-[r:{relationship_type}]->(m)
        SET r += $properties
        RETURN r
        """
        try:
            with self.driver.session() as session:
                session.run(
                    query,
                    user_id=str(user_id),
                    media_id=str(media_id),
                    properties=properties
                )
            logger.info(f"Created {relationship_type} relationship: {user_id} -> {media_id}")
            return True
        except Neo4jError as e:
            logger.error(f"Failed to create relationship: {e}")
            return False

    def delete_collection_relationship(
        self,
        user_id: str,
        media_id: str,
        relationship_type: str
    ) -> bool:
        """
        Delete a relationship between User and Media.

        Args:
            user_id: User UUID
            media_id: Media UUID
            relationship_type: Type of relationship to delete

        Returns:
            bool: Success status
        """
        query = f"""
        MATCH (u:User {{id: $user_id}})-[r:{relationship_type}]->(m:Media {{id: $media_id}})
        DELETE r
        """
        try:
            with self.driver.session() as session:
                session.run(query, user_id=str(user_id), media_id=str(media_id))
            logger.info(f"Deleted {relationship_type} relationship: {user_id} -> {media_id}")
            return True
        except Neo4jError as e:
            logger.error(f"Failed to delete relationship: {e}")
            return False

    def create_genre_relationship(self, media_id: str, genre_name: str) -> bool:
        """
        Create HAS_GENRE relationship between Media and Genre.

        Args:
            media_id: Media UUID
            genre_name: Genre name

        Returns:
            bool: Success status
        """
        query = """
        MATCH (m:Media {id: $media_id})
        MERGE (g:Genre {name: $genre_name})
        MERGE (m)-[r:HAS_GENRE]->(g)
        RETURN r
        """
        try:
            with self.driver.session() as session:
                session.run(query, media_id=str(media_id), genre_name=genre_name)
            logger.info(f"Created HAS_GENRE relationship: {media_id} -> {genre_name}")
            return True
        except Neo4jError as e:
            logger.error(f"Failed to create genre relationship: {e}")
            return False

    # ==================== QUERY OPERATIONS ====================

    def get_node_count(self, label: str) -> int:
        """
        Get count of nodes with a specific label.

        Args:
            label: Node label (User, Media, Genre)

        Returns:
            int: Number of nodes
        """
        query = f"MATCH (n:{label}) RETURN count(n) AS count"
        try:
            with self.driver.session() as session:
                result = session.run(query)
                return result.single()["count"]
        except Neo4jError as e:
            logger.error(f"Failed to get node count: {e}")
            return 0

    def get_user_collection_count(self, user_id: str, relationship_type: Optional[str] = None) -> int:
        """
        Get count of media items in user's collection.

        Args:
            user_id: User UUID
            relationship_type: Optional filter by relationship type

        Returns:
            int: Number of items
        """
        if relationship_type:
            query = f"""
            MATCH (u:User {{id: $user_id}})-[r:{relationship_type}]->(m:Media)
            RETURN count(m) AS count
            """
        else:
            query = """
            MATCH (u:User {id: $user_id})-[r]->(m:Media)
            RETURN count(m) AS count
            """

        try:
            with self.driver.session() as session:
                result = session.run(query, user_id=str(user_id))
                return result.single()["count"]
        except Neo4jError as e:
            logger.error(f"Failed to get collection count: {e}")
            return 0

    def run_custom_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict]:
        """
        Run a custom Cypher query and return results.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            List of result dictionaries
        """
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [dict(record) for record in result]
        except Neo4jError as e:
            logger.error(f"Failed to run custom query: {e}")
            return []

    # ==================== BATCH OPERATIONS ====================

    def batch_create_nodes(self, nodes: List[Dict[str, Any]], label: str) -> bool:
        """
        Create multiple nodes in a single transaction.

        Args:
            nodes: List of node dictionaries with properties
            label: Node label

        Returns:
            bool: Success status
        """
        query = f"""
        UNWIND $nodes AS node
        MERGE (n:{label} {{id: node.id}})
        SET n += node
        """
        try:
            with self.driver.session() as session:
                session.run(query, nodes=nodes)
            logger.info(f"Batch created {len(nodes)} {label} nodes")
            return True
        except Neo4jError as e:
            logger.error(f"Failed to batch create nodes: {e}")
            return False

    # ==================== CONSTRAINTS & INDEXES ====================

    def create_constraints(self) -> bool:
        """
        Create uniqueness constraints for the graph schema.

        Returns:
            bool: Success status
        """
        constraints = [
            "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE",
            "CREATE CONSTRAINT media_id IF NOT EXISTS FOR (m:Media) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT genre_name IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE",
        ]

        try:
            with self.driver.session() as session:
                for constraint in constraints:
                    session.run(constraint)
            logger.info("Created Neo4j constraints")
            return True
        except Neo4jError as e:
            logger.error(f"Failed to create constraints: {e}")
            return False

    def create_indexes(self) -> bool:
        """
        Create indexes for better query performance.

        Returns:
            bool: Success status
        """
        indexes = [
            "CREATE INDEX user_username IF NOT EXISTS FOR (u:User) ON (u.username)",
            "CREATE INDEX media_title IF NOT EXISTS FOR (m:Media) ON (m.title)",
            "CREATE INDEX media_type IF NOT EXISTS FOR (m:Media) ON (m.media_type)",
        ]

        try:
            with self.driver.session() as session:
                for index in indexes:
                    session.run(index)
            logger.info("Created Neo4j indexes")
            return True
        except Neo4jError as e:
            logger.error(f"Failed to create indexes: {e}")
            return False


# Singleton instance
_neo4j_service = None


def get_neo4j_service() -> Neo4jService:
    """
    Get or create a singleton Neo4jService instance.

    Returns:
        Neo4jService: The service instance
    """
    global _neo4j_service
    if _neo4j_service is None:
        _neo4j_service = Neo4jService()
        _neo4j_service.connect()
    return _neo4j_service
