# src/phases/phase_1_3_relationships.py
"""
Phase 1.3: Advanced Relationship Detector

Combines:
1. Explicit FKs (schema)
2. Naming heuristics 
3. Inclusion dependencies (value overlap)
4. Semantic embeddings (future)

Input: Phase 1.1 schema + Phase 1.2 stats
Output: Complete edge definitions
"""
from pathlib import Path
from typing import Dict, Any, List, Tuple
import json
from sqlalchemy.engine import Engine
from sqlalchemy import inspect, text
import pandas as pd
from collections import defaultdict
import re


Relationship = Dict[str, Any]


def run_phase_1_3_relationships(
    engine: Engine,
    client_id: str,
    artifacts_root: Path,
) -> Dict[str, Any]:
    """
    Detect ALL relationships: explicit + heuristic + inclusion.
    """
    # Read Phase 1.1 schema
    phase1_path = artifacts_root / client_id / "01_schema_graph.json"
    with phase1_path.open("r") as f:
        schema = json.load(f)

    # Read Phase 1.2 stats
    phase2_path = artifacts_root / client_id / "02_data_profile.json"
    with phase2_path.open("r") as f:
        profile_data = json.load(f)

    # Transform stats to the expected format and add total_rows
    stats = {}
    for table_name, columns in profile_data.items():
        total_rows = schema["tables"][table_name]["row_count"]
        for column_name, col_stats in columns.items():
            stats[f"{table_name}.{column_name}"] = {
                "table": table_name,
                "column": column_name,
                "total_rows": total_rows,
                **col_stats
            }

    relationships: List[Relationship] = []

    # 1. EXPLICIT FKs (from schema)
    relationships.extend(_extract_explicit_fks(engine))

    # 2. NAMING HEURISTICS
    naming_rels = _detect_naming_relationships(schema, stats)
    relationships.extend(naming_rels)

    # 3. INCLUSION DEPENDENCIES (value overlap)
    inclusion_rels = _detect_inclusion_dependencies(engine, schema, stats)
    relationships.extend(inclusion_rels)

    # Group by source table
    edges_by_source = defaultdict(list)
    for rel in relationships:
        edges_by_source[rel["source_table"]].append(rel)

    result = {
        "client_id": client_id,
        "relationships": relationships,
        "edges_by_source": dict(edges_by_source),
        "summary": {
            "explicit": len([r for r in relationships if r["type"] == "explicit"]),
            "naming": len([r for r in relationships if r["type"] == "naming"]),
            "inclusion": len([r for r in relationships if r["type"] == "inclusion"]),
        }
    }

    # Write Phase 1.3 artifact
    out_dir = artifacts_root / client_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "03_relationships_complete.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    return result


def _extract_explicit_fks(engine: Engine) -> List[Relationship]:
    """Extract explicit foreign key constraints."""
    relationships = []
    
    try:
        with engine.connect() as conn:
            fks = conn.execute(text("""
                SELECT 
                    tc.table_name as child_table,
                    kcu.column_name as child_column,
                    ccu.table_name AS parent_table,
                    ccu.column_name AS parent_column
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
            """)).fetchall()

            for child_table, child_col, parent_table, parent_col in fks:
                relationships.append({
                    "type": "explicit",
                    "source_table": child_table,
                    "source_column": child_col,
                    "target_table": parent_table,
                    "target_column": parent_col,
                    "confidence": 1.0,
                    "evidence": "foreign_key_constraint"
                })
    except Exception as e:
        print(f"Explicit FK extraction failed: {e}")

    return relationships


def _detect_naming_relationships(schema: Dict, stats: Dict) -> List[Relationship]:
    """Detect relationships via naming conventions."""
    relationships = []
    
    # ID column candidates (from stats)
    id_candidates = {}
    for col_key, col_stats in stats.items():
        if _is_likely_id_column(col_stats):
            table_name = col_stats["table"]
            id_candidates[f"{table_name}.id"] = col_key

    # Scan for [table]_id columns
    naming_patterns = [
        r"(.+)_id$",      # table_id
        r"(.+)Id$",       # tableId
        r"^(.+?)_code$",  # table_code
    ]

    for col_key, col_stats in stats.items():
        table_name = col_stats["table"]
        col_name = col_stats["column"]
        
        for pattern in naming_patterns:
            match = re.match(pattern, col_name)
            if match:
                candidate_table = match.group(1)
                candidate_col_key = f"{candidate_table}.id"
                
                if candidate_col_key in id_candidates:
                    relationships.append({
                        "type": "naming",
                        "source_table": table_name,
                        "source_column": col_name,
                        "target_table": candidate_table,
                        "target_column": "id",
                        "confidence": 0.85,
                        "evidence": f"naming_pattern_{pattern}"
                    })
    
    return relationships


def _is_likely_id_column(col_stats: Dict) -> bool:
    """Heuristic: is this column likely a primary key/ID?"""
    col_name = col_stats["column"].lower()
    
    # Name suggests ID
    if any(id_word in col_name for id_word in ["id", "key", "code"]):
        return True
    
    # Stats suggest ID (high cardinality)
    # Handle division by zero if total_rows is 0
    if col_stats["total_rows"] == 0:
        return False # No rows, so cannot be an ID
        
    distinct_pct = col_stats["distinct_count"] / col_stats["total_rows"]
    if distinct_pct > 0.95:
        return True
    
    return False


def _detect_inclusion_dependencies(
    engine: Engine,
    schema: Dict,
    stats: Dict
) -> List[Relationship]:
    """Check if values in ColA are subset of ColB (inclusion dependency)."""
    relationships = []
    
    # Get candidate ID columns (high cardinality)
    candidate_pks = {}
    for col_key, col_stats in stats.items():
        if _is_likely_id_column(col_stats):
            table_name = col_stats["table"]
            candidate_pks[table_name] = col_key

    # For each potential FK column, check overlap with PKs
    for col_key, col_stats in stats.items():
        if col_stats["distinct_count"] < 1000:  # only check low-cardinality columns
            fk_table = col_stats["table"]
            fk_col = col_stats["column"]
            
            for pk_table, pk_col_key in candidate_pks.items():
                if fk_table == pk_table:
                    continue  # same table
                
                overlap_pct = _check_value_overlap(engine, fk_table, fk_col, pk_table, pk_col_key)
                if overlap_pct > 0.90:  # 90% overlap threshold
                    relationships.append({
                        "type": "inclusion",
                        "source_table": fk_table,
                        "source_column": fk_col,
                        "target_table": pk_table,
                        "target_column": pk_col_key.split(".")[2],
                        "confidence": overlap_pct,
                        "evidence": f"value_overlap_{overlap_pct:.1%}"
                    })
    
    return relationships


def _check_value_overlap(
    engine: Engine,
    fk_table: str,
    fk_col: str,
    pk_table: str,
    pk_col_key: str
) -> float:
    """Check % overlap between FK values and PK values."""
    try:
        pk_col = pk_col_key.split(".")[2]
        
        with engine.connect() as conn:
            # Get distinct values from both
            fk_values = set(
                conn.execute(text(f"SELECT DISTINCT {fk_col} FROM {fk_table} WHERE {fk_col} IS NOT NULL"))
                .scalars().all()
            )
            pk_values = set(
                conn.execute(text(f"SELECT {pk_col} FROM {pk_table} WHERE {pk_col} IS NOT NULL LIMIT 1000"))
                .scalars().all()
            )
            
            if not fk_values or not pk_values:
                return 0.0
            
            overlap = len(fk_values & pk_values) / len(fk_values)
            return overlap
            
    except:
        return 0.0
