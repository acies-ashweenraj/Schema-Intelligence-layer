#!/usr/bin/env python3
"""
Phase 1.4: Fingerprinting
Generate table fingerprints: role, risk_profile, clusters, domain flags.
"""

import json
import os
from collections import defaultdict
from typing import Dict, List, Any, Set


class FingerprintEngine:
    """Generate fingerprints for tables: role, risk, clusters."""

    def __init__(self, schema_graph: Dict[str, Any], relationships: Dict[str, List]):
        """Initialize with schema and relationships."""
        self.schema_graph = schema_graph
        self.relationships = relationships

    def _infer_table_role(self, table: str, table_info: Dict) -> str:
        """
        Infer table role based on connectivity and size.
        Roles: hub, dimension, detail, unknown
        """
        row_count = table_info.get("row_count", 0)
        col_count = len(table_info.get("columns", []))

        # Count incoming and outgoing relationships
        incoming_rels = 0
        for t, rels in self.relationships.items():
            for rel in rels:
                refers_to = rel.get("refers_to", "").split(".")[0]
                if refers_to == table:
                    incoming_rels += 1

        outgoing_rels = len(self.relationships.get(table, []))

        # Classification logic
        if row_count > 1000 and incoming_rels >= 3:
            return "hub"
        elif row_count < 1000 and outgoing_rels >= 3:
            return "dimension"
        elif incoming_rels >= 1 and outgoing_rels == 0:
            return "detail"
        else:
            return "unknown"

    def _detect_risk_profile(self, table_info: Dict) -> tuple:
        """
        Detect risk profile from comments.
        Looks for Redline, OSHA, Violation, Critical keywords.
        """
        risk_profile = "low_risk"
        redline_comments = []

        risk_keywords = ["redline", "osha", "violation", "critical", "danger", "incident", "safety"]

        for col in table_info.get("columns", []):
            comment = (col.get("comment") or "").lower()
            if any(keyword in comment for keyword in risk_keywords):
                risk_profile = "high_risk"
                if col.get("comment"):
                    redline_comments.append(col["comment"])

        return risk_profile, redline_comments

    def _detect_domain_flags(self, table_info: Dict) -> tuple:
        """Detect temporal and geospatial flags."""
        col_names = [c["name"].lower() for c in table_info.get("columns", [])]

        temporal_keywords = ["date", "time", "timestamp", "created", "modified", "updated"]
        geospatial_keywords = ["location", "geo", "latitude", "longitude", "coords", "address"]

        has_temporal = any(keyword in name for keyword in temporal_keywords for name in col_names)
        has_geospatial = any(keyword in name for keyword in geospatial_keywords for name in col_names)

        return has_temporal, has_geospatial

    def _bfs_clusters(self) -> List[List[str]]:
        """Find connected components via BFS graph traversal."""
        visited = set()
        clusters = []

        for table in self.schema_graph["tables"].keys():
            if table in visited:
                continue

            # BFS from this table
            cluster = []
            queue = [table]

            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue

                visited.add(current)
                cluster.append(current)

                # Find connected tables (outgoing relationships)
                for rel in self.relationships.get(current, []):
                    target = rel.get("refers_to", "").split(".")[0]
                    if target and target not in visited:
                        queue.append(target)

                # Find connected tables (incoming relationships)
                for t, rels in self.relationships.items():
                    for rel in rels:
                        if rel.get("refers_to", "").split(".")[0] == current and t not in visited:
                            queue.append(t)

            if cluster:
                clusters.append(cluster)

        return clusters

    def generate(self) -> Dict[str, Dict]:
        """Generate fingerprints for all tables."""
        print("\n" + "="*70)
        print("PHASE 1.4: FINGERPRINTING")
        print("="*70)

        fingerprints = {}
        clusters = self._bfs_clusters()

        print(f"✅ Detected {len(clusters)} clusters (connected components)")

        # Create cluster assignments
        cluster_map = {}
        for idx, cluster in enumerate(clusters):
            cluster_name = f"cluster_{idx+1}"
            for table in cluster:
                cluster_map[table] = cluster_name

        # Generate fingerprints
        for table, table_info in self.schema_graph["tables"].items():
            role = self._infer_table_role(table, table_info)
            risk_profile, redline_comments = self._detect_risk_profile(table_info)
            has_temporal, has_geospatial = self._detect_domain_flags(table_info)

            fingerprints[table] = {
                "role": role,
                "risk_profile": risk_profile,
                "redline_comments": redline_comments,
                "cluster": cluster_map.get(table, "orphan"),
                "has_temporal": has_temporal,
                "has_geospatial": has_geospatial
            }

        high_risk = sum(1 for fp in fingerprints.values() if fp["risk_profile"] == "high_risk")
        print(f"✅ Generated fingerprints for {len(fingerprints)} tables")
        print(f"   High-risk tables: {high_risk}")

        return fingerprints

    def save(self, data: Dict, output_path: str) -> None:
        """Save fingerprints to JSON file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Saved: {output_path}")


