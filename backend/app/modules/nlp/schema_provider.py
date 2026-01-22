import json
from pathlib import Path


def load_schema_from_cache() -> str:
    # backend/app/semantic_cache.json
    cache_path = Path(__file__).resolve().parents[2] / "semantic_cache.json"

    if not cache_path.exists():
        raise FileNotFoundError("Schema not available (semantic_cache.json missing)")

    cache = json.loads(cache_path.read_text(encoding="utf-8"))

    tables = cache.get("tables", {})
    cols = cache.get("columns", {})
    rels = cache.get("relationships", {})

    schema_lines = []
    schema_lines.append("NODE LABELS:")
    for table_name, label in tables.items():
        schema_lines.append(f"- {label} (from table: {table_name})")

    schema_lines.append("\nPROPERTIES:")
    for col_name, prop_name in cols.items():
        schema_lines.append(f"- {prop_name} (from column: {col_name})")

    schema_lines.append("\nRELATIONSHIPS:")
    for key, rel_name in rels.items():
        schema_lines.append(f"- {key} => {rel_name}")

    return "\n".join(schema_lines)
