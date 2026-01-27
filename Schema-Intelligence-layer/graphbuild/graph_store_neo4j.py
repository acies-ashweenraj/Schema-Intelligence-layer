import json
import logging
import os
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from neo4j import GraphDatabase, Session, Transaction, AsyncGraphDatabase, AsyncSession
from neo4j.exceptions import Neo4jError, ServiceUnavailable, DriverError
import asyncio
from datetime import datetime
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass
class Neo4jConfig:
    """Neo4j connection configuration."""
    uri: str
    user: str
    password: str
    database: str = "neo4j"
    encrypted: bool = False
    connection_timeout: int = 30
    log_level: str = "WARNING"


class Neo4jGraphStore:
    """
    Synchronous Neo4j Graph Store.
    
    Manages persistent knowledge graph with ACID guarantees, indexing, and clustering support.
    
    Usage:
        store = Neo4jGraphStore(config)
        store.initialize_schema()
        store.load_semantic_layer(semantic_dict, "client_1")
        tables = store.get_related_tables("incident_table", max_hops=3)
        store.close()
    """

    def __init__(self, config: Neo4jConfig):
        """Initialize Neo4j driver and configuration."""
        self.config = config
        self._driver = None
        self._connect()
        logger.info(f"Neo4jGraphStore initialized: {config.uri}")

    def _connect(self) -> None:
        """Establish connection to Neo4j."""
        try:
            self._driver = GraphDatabase.driver(
                self.config.uri,
                auth=(self.config.user, self.config.password),
                encrypted=self.config.encrypted,
                connection_timeout=self.config.connection_timeout,
            )
            # Verify connection
            with self._driver.session(database=self.config.database) as session:
                session.run("RETURN 1")
            logger.info("Neo4j connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self) -> None:
        """Close Neo4j driver."""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j connection closed")

    def initialize_schema(self) -> None:
        """
        Create Neo4j schema (labels, constraints, indexes).
        Run once per Neo4j instance.
        """
        with self._driver.session(database=self.config.database) as session:
            session.execute_write(self._create_schema_tx)
        logger.info("Neo4j schema initialized")

    @staticmethod
    def _create_schema_tx(tx: Transaction) -> None:
        """Create schema: labels, constraints, indexes."""

        # Create uniqueness constraints (also creates indexes)
        constraints = [
            "CREATE CONSTRAINT table_client_name IF NOT EXISTS FOR (t:Table) REQUIRE (t.client_id, t.name) IS UNIQUE",
            "CREATE CONSTRAINT column_client_table_name IF NOT EXISTS FOR (c:Column) REQUIRE (c.client_id, c.table, c.name) IS UNIQUE",
        ]

        for constraint in constraints:
            try:
                tx.run(constraint)
                logger.debug(f"Created constraint: {constraint[:50]}...")
            except Neo4jError as e:
                if "already exists" not in str(e):
                    logger.warning(f"Constraint creation issue: {e}")

        # Create indexes for common queries
        indexes = [
            "CREATE INDEX table_role IF NOT EXISTS FOR (t:Table) ON (t.role)",
            "CREATE INDEX table_risk IF NOT EXISTS FOR (t:Table) ON (t.risk_category)",
            "CREATE INDEX column_type IF NOT EXISTS FOR (c:Column) ON (c.data_type)",
            "CREATE INDEX column_risk IF NOT EXISTS FOR (c:Column) ON (c.risk_category)",
        ]

        for index in indexes:
            try:
                tx.run(index)
                logger.debug(f"Created index: {index[:50]}...")
            except Neo4jError as e:
                if "already exists" not in str(e):
                    logger.warning(f"Index creation issue: {e}")

    def load_semantic_layer(self, semantic_layer: Dict[str, Any], client_id: str) -> None:
        """
        Load semantic layer JSON into Neo4j graph.
        Creates Table nodes, Column nodes, and FK relationships.
        Idempotent: Safe to run multiple times.
        
        Args:
            semantic_layer: Dict from semantic_layer_complete.json
            client_id: Unique identifier for this client (e.g., "c1ehs_oilgas")
        """
        with self._driver.session(database=self.config.database) as session:
            session.execute_write(self._load_semantic_layer_tx, semantic_layer, client_id)
        logger.info(f"Loaded semantic layer for client {client_id}")

    @staticmethod
    def _load_semantic_layer_tx(tx: Transaction, semantic_layer: Dict, client_id: str) -> None:
        """Transaction: Load tables, columns, and relationships."""

        tables_dict = semantic_layer.get("tables", {})
        
        all_columns = []
        all_relationships_data = []
        fk_columns = set() # To store (table_name, column_name) of FKs

        # 1. Collect all columns and relationships and identify FK columns
        for table_name, table_data in tables_dict.items():
            if "columns" in table_data:
                for column in table_data["columns"]:
                    # Add table name to column for easier processing
                    col_copy = column.copy()
                    col_copy["table"] = table_name
                    all_columns.append(col_copy)

            if "relationships" in table_data:
                for rel in table_data["relationships"]:
                    # Store original relationship data
                    all_relationships_data.append(rel)
                    # Add source and target columns to fk_columns set
                    fk_columns.add((rel.get("source_table"), rel.get("source_column")))
                    fk_columns.add((rel.get("target_table"), rel.get("target_column")))

        # 2. Create Table nodes
        for table_name, table_data in tables_dict.items():
            tx.run(
                """
                MERGE (t:Table {client_id: $client_id, name: $name})
                ON CREATE SET 
                    t.role = $role,
                    t.description = $description,
                    t.risk_category = $risk_category,
                    t.record_count = $record_count,
                    t.is_pii = $is_pii,
                    t.created_at = datetime(),
                    t.last_updated = datetime()
                ON MATCH SET
                    t.role = $role,
                    t.description = $description,
                    t.risk_category = $risk_category,
                    t.record_count = $record_count,
                    t.is_pii = $is_pii,
                    t.last_updated = datetime()
                """,
                client_id=client_id,
                name=table_data.get("name"),
                role=table_data.get("role", "UNKNOWN"),
                description=table_data.get("description", ""),
                risk_category=table_data.get("risk_profile", "low_risk"),
                record_count=table_data.get("row_count", 0),
                is_pii=False, # `is_pii` is not in JSON, defaulting to False
            )

        # 3. Create Column nodes
        for column in all_columns:
            # Determine if column is an FK based on the collected set
            is_fk = (column.get("table"), column.get("name")) in fk_columns
            
            tx.run(
                """
                MERGE (c:Column {client_id: $client_id, table: $table, name: $name})
                ON CREATE SET 
                    c.data_type = $data_type,
                    c.nullable = $nullable,
                    c.description = $description,
                    c.risk_category = $risk_category,
                    c.is_pk = $is_pk,
                    c.is_fk = $is_fk,
                    c.patterns = $patterns,
                    c.null_percent = $null_percent,
                    c.distinct_count = $distinct_count,
                    c.created_at = datetime(),
                    c.last_updated = datetime()
                ON MATCH SET
                    c.data_type = $data_type,
                    c.nullable = $nullable,
                    c.description = $description,
                    c.risk_category = $risk_category,
                    c.is_pk = $is_pk,
                    c.is_fk = $is_fk,
                    c.patterns = $patterns,
                    c.null_percent = $null_percent,
                    c.distinct_count = $distinct_count,
                    c.last_updated = datetime()
                """,
                client_id=client_id,
                table=column.get("table"),
                name=column.get("name"),
                data_type=column.get("data_type", "UNKNOWN"),
                nullable=column.get("nullable", True),
                description=column.get("comment", ""),
                risk_category="LOW", # `risk_category` for columns is not in JSON, defaulting to LOW
                is_pk=column.get("is_key", False),
                is_fk=is_fk,
                patterns=json.dumps(column.get("samples", [])),
                null_percent=column.get("null_pct", 0.0),
                distinct_count=column.get("distinct_pct", 0.0),
            )

        # 4. Create COLUMN_OF relationships (Column -> Table)
        tx.run(
            """
            MATCH (c:Column {client_id: $client_id})
            MATCH (t:Table {client_id: $client_id, name: c.table})
            MERGE (c)-[:COLUMN_OF]->(t)
            """,
            client_id=client_id,
        )

        # 5. Create FK relationships (Table -> Table)
        for rel_data in all_relationships_data:
            if rel_data.get("type") == "explicit":
                tx.run(
                    """
                    MATCH (from_t:Table {client_id: $client_id, name: $from_table})
                    MATCH (to_t:Table {client_id: $client_id, name: $to_table})
                    MERGE (from_t)-[fk:FK]->(to_t)
                    ON CREATE SET 
                        fk.from_column = $from_column,
                        fk.to_column = $to_column,
                        fk.cardinality = $cardinality
                    ON MATCH SET
                        fk.from_column = $from_column,
                        fk.to_column = $to_column,
                        fk.cardinality = $cardinality
                    """,
                    client_id=client_id,
                    from_table=rel_data.get("source_table"),
                    to_table=rel_data.get("target_table"),
                    from_column=rel_data.get("source_column"),
                    to_column=rel_data.get("target_column"),
                    cardinality="1:N", # Cardinality is not in the JSON, so I'm using a default
                )

    def get_related_tables(
        self, client_id: str, table_name: str, max_hops: int = 3, direction: str = "BOTH"
    ) -> List[str]:
        """
        Find all tables related to a given table through FK relationships.
        
        Args:
            client_id: Client identifier
            table_name: Starting table name
            max_hops: Max relationship hops to traverse
            direction: "BOTH", "OUT" (forward), "IN" (backward)
        
        Returns:
            List of related table names
        """
        with self._driver.session(database=self.config.database) as session:
            result = session.execute_read(
                self._get_related_tables_read, client_id, table_name, max_hops, direction
            )
            return result

    @staticmethod
    def _get_related_tables_read(
        tx: Transaction, client_id: str, table_name: str, max_hops: int, direction: str
    ) -> List[str]:
        """Read transaction: Query related tables using Cypher."""

        if direction == "BOTH":
            rel_pattern = f"-[r:FK*1..{max_hops}]-"
        elif direction == "OUT":
            rel_pattern = f"-[r:FK*1..{max_hops}]->"
        else:  # IN
            rel_pattern = f"<-[r:FK*1..{max_hops}]-"

        if direction == "BOTH":
            query = f"""
            MATCH (t:Table {{client_id: $client_id, name: $table_name}})
            MATCH (t){rel_pattern}(related:Table {{client_id: $client_id}})
            RETURN DISTINCT related.name AS name
            """
        elif direction == "OUT":
            query = f"""
            MATCH (t:Table {{client_id: $client_id, name: $table_name}})
            MATCH (t){rel_pattern}(related:Table {{client_id: $client_id}})
            RETURN DISTINCT related.name AS name
            """
        else:  # IN
            query = f"""
            MATCH (t:Table {{client_id: $client_id, name: $table_name}})
            MATCH (t){rel_pattern}(related:Table {{client_id: $client_id}})
            RETURN DISTINCT related.name AS name
            """

        result = tx.run(query, client_id=client_id, table_name=table_name)
        return [record["name"] for record in result]

    def get_column_metadata(
        self, client_id: str, table_name: str, column_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get full metadata for a specific column.
        
        Args:
            client_id: Client identifier
            table_name: Table name
            column_name: Column name
        
        Returns:
            Dict with column metadata or None if not found
        """
        with self._driver.session(database=self.config.database) as session:
            result = session.execute_read(
                self._get_column_metadata_read, client_id, table_name, column_name
            )
            return result

    @staticmethod
    def _get_column_metadata_read(
        tx: Transaction, client_id: str, table_name: str, column_name: str
    ) -> Optional[Dict[str, Any]]:
        """Read transaction: Get column metadata."""

        query = """
        MATCH (c:Column {client_id: $client_id, table: $table_name, name: $column_name})
        RETURN c
        """

        record = tx.run(
            query, client_id=client_id, table_name=table_name, column_name=column_name
        ).single()

        if not record:
            return None

        col_node = record["c"]
        metadata = dict(col_node)

        # Parse JSON patterns if stored as string
        if "patterns" in metadata and isinstance(metadata["patterns"], str):
            try:
                metadata["patterns"] = json.loads(metadata["patterns"])
            except json.JSONDecodeError:
                metadata["patterns"] = []

        return metadata

    def get_table_metadata(self, client_id: str, table_name: str) -> Optional[Dict[str, Any]]:
        """Get full metadata for a specific table."""
        with self._driver.session(database=self.config.database) as session:
            result = session.execute_read(
                self._get_table_metadata_read, client_id, table_name
            )
            return result

    @staticmethod
    def _get_table_metadata_read(
        tx: Transaction, client_id: str, table_name: str
    ) -> Optional[Dict[str, Any]]:
        """Read transaction: Get table metadata."""

        query = """
        MATCH (t:Table {client_id: $client_id, name: $table_name})
        RETURN t
        """

        record = tx.run(query, client_id=client_id, table_name=table_name).single()

        if not record:
            return None

        return dict(record["t"])

    def get_fk_relationships(
        self, client_id: str, table_name: str
    ) -> List[Dict[str, str]]:
        """
        Get all FK relationships for a table (as source or target).
        
        Returns:
            List of dicts: {from_table, to_table, from_column, to_column, cardinality}
        """
        with self._driver.session(database=self.config.database) as session:
            result = session.execute_read(
                self._get_fk_relationships_read, client_id, table_name
            )
            return result

    @staticmethod
    def _get_fk_relationships_read(
        tx: Transaction, client_id: str, table_name: str
    ) -> List[Dict[str, str]]:
        """Read transaction: Get FK relationships."""

        query = """
        MATCH (from_t:Table {client_id: $client_id, name: $table_name})
        -[fk:FK]->(to_t:Table {client_id: $client_id})
        RETURN 
            from_t.name AS from_table,
            to_t.name AS to_table,
            fk.from_column AS from_column,
            fk.to_column AS to_column,
            fk.cardinality AS cardinality
        
        UNION
        
        MATCH (to_t:Table {client_id: $client_id, name: $table_name})
        <-[fk:FK]-(from_t:Table {client_id: $client_id})
        RETURN 
            from_t.name AS from_table,
            to_t.name AS to_table,
            fk.from_column AS from_column,
            fk.to_column AS to_column,
            fk.cardinality AS cardinality
        """

        result = tx.run(query, client_id=client_id, table_name=table_name)
        return [dict(record) for record in result]

    def search_by_pattern(
        self, client_id: str, pattern_type: str
    ) -> List[Dict[str, Any]]:
        """
        Find all columns matching a pattern type (e.g., "ID", "DATE", "EMAIL").
        
        Args:
            client_id: Client identifier
            pattern_type: Pattern type (ID, DATE, EMAIL, BINARY, ENUM)
        
        Returns:
            List of column metadata dicts
        """
        with self._driver.session(database=self.config.database) as session:
            result = session.execute_read(
                self._search_by_pattern_read, client_id, pattern_type
            )
            return result

    @staticmethod
    def _search_by_pattern_read(
        tx: Transaction, client_id: str, pattern_type: str
    ) -> List[Dict[str, Any]]:
        """Read transaction: Search columns by pattern."""

        query = """
        MATCH (c:Column {client_id: $client_id})
        WHERE c.patterns CONTAINS $pattern_type
        RETURN c
        """

        result = tx.run(query, client_id=client_id, pattern_type=pattern_type)
        columns = []
        for record in result:
            col = dict(record["c"])
            if "patterns" in col and isinstance(col["patterns"], str):
                try:
                    col["patterns"] = json.loads(col["patterns"])
                except json.JSONDecodeError:
                    col["patterns"] = []
            columns.append(col)
        return columns

    def get_high_risk_columns(self, client_id: str) -> List[Dict[str, Any]]:
        """Get all HIGH-risk columns for a client."""
        with self._driver.session(database=self.config.database) as session:
            result = session.execute_read(
                self._get_high_risk_columns_read, client_id
            )
            return result

    @staticmethod
    def _get_high_risk_columns_read(tx: Transaction, client_id: str) -> List[Dict[str, Any]]:
        """Read transaction: Get high-risk columns."""

        query = """
        MATCH (c:Column {client_id: $client_id, risk_category: 'HIGH'})
        RETURN c
        """

        result = tx.run(query, client_id=client_id)
        return [dict(record["c"]) for record in result]

    def get_pii_tables(self, client_id: str) -> List[Dict[str, Any]]:
        """Get all tables marked as PII."""
        with self._driver.session(database=self.config.database) as session:
            result = session.execute_read(self._get_pii_tables_read, client_id)
            return result

    @staticmethod
    def _get_pii_tables_read(tx: Transaction, client_id: str) -> List[Dict[str, Any]]:
        """Read transaction: Get PII tables."""

        query = """
        MATCH (t:Table {client_id: $client_id, is_pii: true})
        RETURN t
        """

        result = tx.run(query, client_id=client_id)
        return [dict(record["t"]) for record in result]

    def get_graph_stats(self, client_id: str) -> Dict[str, int]:
        """Get basic graph statistics for a client."""
        with self._driver.session(database=self.config.database) as session:
            result = session.execute_read(self._get_graph_stats_read, client_id)
            return result

    @staticmethod
    def _get_graph_stats_read(tx: Transaction, client_id: str) -> Dict[str, int]:
        """Read transaction: Get graph statistics."""

        query = """
        MATCH (t:Table {client_id: $client_id})
        WITH COUNT(DISTINCT t) AS table_count
        MATCH (c:Column {client_id: $client_id})
        WITH table_count, COUNT(DISTINCT c) AS column_count
        MATCH (t:Table {client_id: $client_id})-[fk:FK]->(:Table {client_id: $client_id})
        RETURN 
            table_count,
            column_count,
            COUNT(DISTINCT fk) AS relationship_count
        """

        record = tx.run(query, client_id=client_id).single()

        if not record:
            return {"tables": 0, "columns": 0, "relationships": 0}

        return {
            "tables": record["table_count"],
            "columns": record["column_count"],
            "relationships": record["relationship_count"],
        }

    def clear_client_data(self, client_id: str) -> None:
        """
        Delete all nodes/relationships for a client.
        Use with caution!
        """
        with self._driver.session(database=self.config.database) as session:
            session.execute_write(self._clear_client_data_tx, client_id)
        logger.warning(f"Cleared all data for client {client_id}")

    @staticmethod
    def _clear_client_data_tx(tx: Transaction, client_id: str) -> None:
        """Transaction: Delete client data."""

        query = """
        MATCH (n {client_id: $client_id})
        DETACH DELETE n
        """

        result = tx.run(query, client_id=client_id)
        summary = result.consume()
        logger.info(f"Deleted {summary.counters.nodes_deleted} nodes, "
                   f"{summary.counters.relationships_deleted} relationships")

    def export_client_graph_cypher(self, client_id: str) -> str:
        """Export client graph as Cypher CREATE statements (for backup/migration)."""
        with self._driver.session(database=self.config.database) as session:
            result = session.execute_read(
                self._export_client_graph_cypher_read, client_id
            )
            return result

    @staticmethod
    def _export_client_graph_cypher_read(tx: Transaction, client_id: str) -> str:
        """Read transaction: Export graph as Cypher."""

        lines = []

        # Export nodes
        query = """
        MATCH (n {client_id: $client_id})
        RETURN n
        """

        result = tx.run(query, client_id=client_id)
        for record in result:
            node = record["n"]
            labels = ":".join(node.labels)
            props = json.dumps(dict(node))
            lines.append(f"CREATE ({labels} {props})")

        # Export relationships
        rel_query = """
        MATCH (from {client_id: $client_id})-[r]->(to {client_id: $client_id})
        RETURN from, r, to
        """

        result = tx.run(rel_query, client_id=client_id)
        for record in result:
            from_node = record["from"]
            rel = record["r"]
            to_node = record["to"]
            props = json.dumps(dict(rel))
            lines.append(
                f"MATCH (from:{from_node.labels[0]} {{name: '{from_node['name']}'}}), "
                f"(to:{to_node.labels[0]} {{name: '{to_node['name']}'}}) "
                f"CREATE (from)-[:{rel.type} {props}]->(to)"
            )

        return "\n".join(lines)


# ============================================================================ 
# ASYNC VERSION (Optional: for Phase 3 with async FastAPI)
# ============================================================================ 


class AsyncNeo4jGraphStore:
    """
    Asynchronous Neo4j Graph Store for non-blocking I/O in FastAPI.
    
    Same interface as Neo4jGraphStore but with async methods.
    Use when integrating with async frameworks like FastAPI.
    """

    def __init__(self, config: Neo4jConfig):
        """Initialize async Neo4j driver."""
        self.config = config
        self._driver = None
        asyncio.run(self._connect_async())
        logger.info(f"AsyncNeo4jGraphStore initialized: {config.uri}")

    async def _connect_async(self) -> None:
        """Establish async connection to Neo4j."""
        try:
            self._driver = AsyncGraphDatabase.driver(
                self.config.uri,
                auth=(self.config.user, self.config.password),
                encrypted=self.config.encrypted,
                connection_timeout=self.config.connection_timeout,
                max_pool_size=self.config.max_pool_size,
            )
            # Verify connection
            async with self._driver.session(database=self.config.database) as session:
                await session.run("RETURN 1")
            logger.info("Async Neo4j connection established")
        except Exception as e:
            logger.error(f"Failed to connect to async Neo4j: {e}")
            raise

    async def close(self) -> None:
        """Close async Neo4j driver."""
        if self._driver:
            await self._driver.close()
            logger.info("Async Neo4j connection closed")

    async def get_related_tables_async(
        self, client_id: str, table_name: str, max_hops: int = 3
    ) -> List[str]:
        """Async: Find related tables."""
        async with self._driver.session(database=self.config.database) as session:
            result = await session.execute_read(
                self._get_related_tables_async_read, client_id, table_name, max_hops
            )
            return result

    @staticmethod
    async def _get_related_tables_async_read(
        tx: Transaction, client_id: str, table_name: str, max_hops: int
    ) -> List[str]:
        """Async read transaction: Get related tables."""

        query = f"""
        MATCH (t:Table {{client_id: $client_id, name: $table_name}})
        MATCH (t)-[r:FK*1..{max_hops}]-(related:Table {{client_id: $client_id}})
        RETURN DISTINCT related.name AS name
        """

        result = await tx.run(query, client_id=client_id, table_name=table_name)
        return [record["name"] async for record in result]


if __name__ == "__main__":
    # Example usage and testing
    logging.basicConfig(level=logging.INFO)
    load_dotenv() # Load environment variables from .env

    # Configuration from environment variables
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password") # Default to 'password' if not in .env, for example's sake.

    if not password:
        logger.error("NEO4J_PASSWORD not found in .env file. Please provide it.")
        exit(1) # Exit if password is not set

    config = Neo4jConfig(
        uri=uri,
        user=user,
        password=password,
        database="neo4j",
    )

    # Initialize
    store = Neo4jGraphStore(config)

    try:
        # Create schema
        store.initialize_schema()

        # Load sample semantic layer (you would load from JSON file)
        sample_semantic = {
            "tables": [
                {
                    "name": "incidents",
                    "role": "FACT",
                    "description": "EHS incident records",
                    "risk_category": "HIGH",
                    "record_count": 10000,
                    "is_pii": True,
                },
                {
                    "name": "locations",
                    "role": "DIMENSION",
                    "description": "Physical locations",
                    "risk_category": "LOW",
                    "record_count": 500,
                    "is_pii": False,
                },
            ],
            "columns": [
                {
                    "table": "incidents",
                    "name": "incident_id",
                    "data_type": "UUID",
                    "is_pk": True,
                    "risk_category": "HIGH",
                    "patterns": ["ID"],
                },
                {
                    "table": "incidents",
                    "name": "location_id",
                    "data_type": "INT",
                    "is_fk": True,
                    "risk_category": "LOW",
                },
            ],
            "relationships": [
                {
                    "type": "FK",
                    "from_table": "incidents",
                    "to_table": "locations",
                    "from_column": "location_id",
                    "to_column": "location_id",
                    "cardinality": "N:1",
                }
            ],
        }

        store.load_semantic_layer(sample_semantic, "c1_test")

        # Test queries
        related = store.get_related_tables("c1_test", "incidents")
        print(f"Related tables: {related}")

        stats = store.get_graph_stats("c1_test")
        print(f"Graph stats: {stats}")

        col_meta = store.get_column_metadata("c1_test", "incidents", "incident_id")
        print(f"Column metadata: {col_meta}")

    finally:
        store.close()
