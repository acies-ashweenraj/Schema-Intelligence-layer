#!/usr/bin/env python3
"""
Phase 1.1: Schema Extraction
Extract all tables, columns, foreign keys, indexes, and row counts from database.
"""

import json
import os
from sqlalchemy import inspect, text
from typing import Dict, List, Any


class SchemaExtractor:
    """Extract complete database schema structure."""

    def __init__(self, engine):
        """Initialize with SQLAlchemy engine."""
        self.engine = engine
        self.inspector = inspect(self.engine)

    def _get_cardinality(self, fk: Dict, unique_constraints: List[Dict]) -> str:
        """Determine cardinality: 1:1 or 1:n based on unique constraints."""
        fk_cols = set(fk['constrained_columns'])
        for uq in unique_constraints:
            if set(uq['column_names']) == fk_cols:
                return "1:1"
        return "1:n"

    def extract(self) -> Dict[str, Any]:
        """Extract all schema information from database."""
        print("\n" + "="*70)
        print("PHASE 1.1: SCHEMA EXTRACTION")
        print("="*70)

        schema_graph = {"tables": {}}
        table_names = self.inspector.get_table_names()

        print(f"📊 Found {len(table_names)} tables in database")

        for table in table_names:
            # Get metadata
            pk = self.inspector.get_pk_constraint(table)
            unique_cons = self.inspector.get_unique_constraints(table)
            indexes = self.inspector.get_indexes(table)

            # Get row count
            row_count = 0
            try:
                with self.engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    row_count = result.scalar() or 0
            except Exception as e:
                print(f"  ⚠️  Could not count rows in {table}: {e}")
                row_count = 0

            # Extract columns
            columns_data = []
            for col in self.inspector.get_columns(table):
                comment = col.get('comment', None)
                columns_data.append({
                    "name": col['name'],
                    "type": str(col['type']),
                    "nullable": col['nullable'],
                    "comment": comment,
                    "default": str(col['default']) if col['default'] else None
                })

            # Extract relationships (Foreign Keys)
            rels_data = []
            for fk in self.inspector.get_foreign_keys(table):
                cardinality = self._get_cardinality(fk, unique_cons)
                rels_data.append({
                    "type": "Foreign Key",
                    "columns": fk['constrained_columns'],
                    "refers_to": f"{fk['referred_table']}.{fk['referred_columns'][0]}",
                    "cardinality": cardinality
                })

            # Build table node
            schema_graph["tables"][table] = {
                "name": table,
                "row_count": row_count,
                "column_count": len(columns_data),
                "primary_key": pk.get('constrained_columns', []),
                "columns": columns_data,
                "relationships": rels_data,
                "indexes": [
                    {
                        "name": i['name'],
                        "columns": i['column_names'],
                        "unique": i['unique']
                    }
                    for i in indexes
                ]
            }

        total_cols = sum(t['column_count'] for t in schema_graph['tables'].values())
        print(f"✅ Extracted {len(schema_graph['tables'])} tables")
        print(f"   Total columns: {total_cols}")

        return schema_graph

    def save(self, data: Dict, output_path: str) -> None:
        """Save schema graph to JSON file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Saved: {output_path}")


if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    sys.path.insert(0, str(Path(__file__).resolve().parents[2])) # Adjust path for Config import
    from src.config import Config

    load_dotenv() # Load environment variables

    # Prompt user for client ID or use a default
    client_id = input("Enter client ID (e.g., c1ehs_oilgas or C2_CONSTRUCTION) for Schema Extractor: ").strip()
    if not client_id:
        client_id = "C2_CONSTRUCTION" # Default for standalone execution
        print(f"No client ID provided, using default: {client_id}")

    try:
        Config.set_client_id(client_id)
        extractor = SchemaExtractor(Config.get_engine())
        schema = extractor.extract()
        output_path = os.path.join(Config._client_config.client_artifacts_dir, "01_schema_graph.json")
        extractor.save(schema, output_path)
    except Exception as e:
        print(f"Error during standalone execution of SchemaExtractor: {e}")
        sys.exit(1)
