#!/usr/bin/env python3
"""
Phase 1.3: Relationship Detection
Detect relationships using multiple methods: explicit FK, naming patterns, overlap, etc.
"""

import json
import os
from collections import defaultdict
from typing import Dict, List, Any


class RelationshipDetector:
    """Detect relationships between tables using multiple methods."""

    def __init__(self, schema_graph: Dict[str, Any]):
        """Initialize with schema graph."""
        self.schema_graph = schema_graph
        self.relationships = defaultdict(list)

    def _detect_explicit_fks(self) -> int:
        """Method 1: Detect explicit Foreign Keys from schema."""
        count = 0
        for table, table_info in self.schema_graph["tables"].items():
            for rel in table_info.get("relationships", []):
                self.relationships[table].append({
                    "method": "explicit_fk",
                    "confidence": 1.0,
                    **rel
                })
                count += 1
        return count

    def _detect_naming_patterns(self) -> int:
        """Method 2: Detect naming patterns (table_id → table.id)."""
        count = 0
        table_names = set(self.schema_graph["tables"].keys())

        for table, table_info in self.schema_graph["tables"].items():
            for col in table_info.get("columns", []):
                col_name_lower = col["name"].lower()

                # Check if column name matches pattern: {table}_id
                for other_table in table_names:
                    if other_table == table:
                        continue

                    pattern = f"{other_table.lower()}_id"
                    if col_name_lower == pattern:
                        self.relationships[table].append({
                            "method": "naming_pattern",
                            "confidence": 0.85,
                            "type": "Named FK",
                            "columns": [col["name"]],
                            "refers_to": f"{other_table}.id",
                            "cardinality": "n:1"
                        })
                        count += 1
        return count

    def _detect_value_overlap(self) -> int:
        """Method 3: Detect relationships via value overlap (>90% containment)."""
        # Placeholder for future implementation
        # This would require actual data sampling
        return 0

    def _detect_junction_tables(self) -> int:
        """Method 4: Detect junction/bridge tables (exactly 2 FK columns)."""
        count = 0
        for table, table_info in self.schema_graph["tables"].items():
            fk_count = len(table_info.get("relationships", []))
            col_count = len(table_info.get("columns", []))

            # Junction table: 2 FKs, small number of columns, small row count
            if fk_count == 2 and col_count <= 5:
                table_info["junction_table"] = True
                count += 1

        return count

    def detect_all(self) -> Dict[str, List[Dict]]:
        """Detect all relationships using multiple methods."""
        print("\n" + "="*70)
        print("PHASE 1.3: RELATIONSHIP DETECTION")
        print("="*70)

        explicit_count = self._detect_explicit_fks()
        naming_count = self._detect_naming_patterns()
        overlap_count = self._detect_value_overlap()
        junction_count = self._detect_junction_tables()

        total = explicit_count + naming_count + overlap_count + junction_count

        print(f"✅ Detected relationships:")
        print(f"   Method 1 (Explicit FK):    {explicit_count}")
        print(f"   Method 2 (Naming Pattern): {naming_count}")
        print(f"   Method 3 (Value Overlap):  {overlap_count}")
        print(f"   Method 4 (Junction):       {junction_count}")
        print(f"   ─────────────────────────")
        print(f"   Total:                     {total}")

        return dict(self.relationships)

    def save(self, data: Dict, output_path: str) -> None:
        """Save relationships to JSON file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Saved: {output_path}")


if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2])) # Adjust path for Config import
    from src.config import Config
    from src.phases.phase_1_1_schema_extractor import SchemaExtractor

    load_dotenv() # Load environment variables

    # Prompt user for client ID or use a default
    client_id = input("Enter client ID (e.g., c1ehs_oilgas or C2_CONSTRUCTION) for Relationship Detector: ").strip()
    if not client_id:
        client_id = "C2_CONSTRUCTION" # Default for standalone execution
        print(f"No client ID provided, using default: {client_id}")

    try:
        Config.set_client_id(client_id)
        
        # Load schema first (it should have been generated by Phase 1.1)
        schema_path = Config._client_config.client_artifacts_dir / "01_schema_graph.json"
        if not schema_path.exists():
            print(f"Schema graph not found at {schema_path}. Running SchemaExtractor...")
            extractor = SchemaExtractor(Config.get_engine())
            schema = extractor.extract()
            extractor.save(schema, str(schema_path))
        else:
            with open(schema_path, 'r') as f:
                schema = json.load(f)

        # Detect relationships
        detector = RelationshipDetector(schema)
        relationships = detector.detect_all()
        output_path = Config._client_config.client_artifacts_dir / "03_relationships_complete.json"
        detector.save(relationships, str(output_path))
    except Exception as e:
        print(f"Error during standalone execution of RelationshipDetector: {e}")
        sys.exit(1)
