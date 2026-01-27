#!/usr/bin/env python3
"""
Phase 1.5: Semantic Layer Assembly
Merge all previous phases (1.1-1.4) into final semantic_layer_complete.json
"""

import json
import os
import decimal
from datetime import datetime, date
from typing import Dict, List, Any


# Custom JSON encoder for Decimal, datetime and date objects
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)



class SemanticLayerAssembler:
    """Assemble final semantic layer from all phases."""

    def __init__(
        self,
        schema_graph: Dict[str, Any],
        profile_data: Dict[str, Dict],
        relationships: Dict[str, List],
        fingerprints: Dict[str, Dict]
    ):
        """Initialize with data from all phases."""
        self.schema_graph = schema_graph
        self.profile_data = profile_data
        self.relationships = relationships
        self.fingerprints = fingerprints

    def assemble(self) -> Dict[str, Any]:
        """Assemble semantic layer from all phases."""
        print("\n" + "="*70)
        print("PHASE 1.5: SEMANTIC LAYER ASSEMBLY")
        print("="*70)

        semantic_layer = {
            "version": "1.5",
            "tables": {}
        }

        for table, table_info in self.schema_graph["tables"].items():
            fingerprint = self.fingerprints.get(table, {})
            table_profile = self.profile_data.get(table, {})

            # Build table entry
            table_entry = {
                # From Phase 1.1 (Schema)
                "name": table,
                "row_count": table_info["row_count"],
                "column_count": table_info["column_count"],
                "primary_key": table_info.get("primary_key", []),

                # From Phase 1.4 (Fingerprint)
                "role": fingerprint.get("role", "unknown"),
                "risk_profile": fingerprint.get("risk_profile", "low_risk"),
                "redline_comments": fingerprint.get("redline_comments", []),
                "cluster": fingerprint.get("cluster", "orphan"),
                "has_temporal": fingerprint.get("has_temporal", False),
                "has_geospatial": fingerprint.get("has_geospatial", False),

                # Columns (combined 1.1, 1.2 data)
                "columns": []
            }

            # Process columns
            for col in table_info["columns"]:
                col_name = col["name"]
                col_profile = table_profile.get(col_name, {})

                col_entry = {
                    "name": col_name,
                    "data_type": col["type"],
                    "nullable": col["nullable"],
                    "comment": col.get("comment"),
                    "is_key": col_name in table_info.get("primary_key", []),

                    # From Phase 1.2 (Profile)
                    "null_pct": col_profile.get("null_pct"),
                    "distinct_pct": self._calculate_distinct_pct(
                        col_profile.get("distinct_count", 0),
                        table_info["row_count"]
                    ),
                    "min": col_profile.get("min"),
                    "max": col_profile.get("max"),
                    "samples": col_profile.get("samples", []),
                }

                table_entry["columns"].append(col_entry)

            # Relationships (from Phase 1.3)
            table_entry["relationships"] = self.relationships.get(table, [])

            semantic_layer["tables"][table] = table_entry

        # Add summary statistics
        semantic_layer["summary"] = self._generate_summary(semantic_layer)

        total_cols = sum(t["column_count"] for t in semantic_layer["tables"].values())
        total_rels = sum(len(r) for r in self.relationships.values())
        high_risk = sum(
            1 for t in semantic_layer["tables"].values()
            if t["risk_profile"] == "high_risk"
        )

        print(f"✅ Assembled semantic layer:")
        print(f"   Tables: {len(semantic_layer['tables'])}")
        print(f"   Columns: {total_cols}")
        print(f"   Relationships: {total_rels}")
        print(f"   High-risk tables: {high_risk}")

        return semantic_layer

    def _calculate_distinct_pct(self, distinct_count: int, total_rows: int) -> float:
        """Calculate distinct percentage."""
        if total_rows <= 0:
            return None
        return round(100 * distinct_count / total_rows, 2)

    def _generate_summary(self, semantic_layer: Dict) -> Dict[str, Any]:
        """Generate summary statistics."""
        tables = semantic_layer["tables"]

        total_cols = sum(t["column_count"] for t in tables.values())
        total_rels = sum(len(t["relationships"]) for t in tables.values())
        high_risk_tables = sum(
            1 for t in tables.values() if t["risk_profile"] == "high_risk"
        )
        orphan_tables = sum(
            1 for t in tables.values() if t["cluster"] == "orphan"
        )

        # Count by role
        hub_tables = sum(1 for t in tables.values() if t["role"] == "hub")
        dimension_tables = sum(1 for t in tables.values() if t["role"] == "dimension")
        detail_tables = sum(1 for t in tables.values() if t["role"] == "detail")

        # Count temporal/geospatial
        temporal_tables = sum(1 for t in tables.values() if t["has_temporal"])
        geospatial_tables = sum(1 for t in tables.values() if t["has_geospatial"])

        return {
            "total_tables": len(tables),
            "total_columns": total_cols,
            "total_relationships": total_rels,
            "high_risk_tables": high_risk_tables,
            "orphan_tables": orphan_tables,
            "hub_tables": hub_tables,
            "dimension_tables": dimension_tables,
            "detail_tables": detail_tables,
            "temporal_tables": temporal_tables,
            "geospatial_tables": geospatial_tables
        }

    def save(self, data: Dict, output_path: str) -> None:
        """Save semantic layer to JSON file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, cls=CustomEncoder)
        print(f"💾 Saved: {output_path}")


