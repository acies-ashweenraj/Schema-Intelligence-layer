import json
from pathlib import Path


def load_semantic_cache(cache_path: str | None = None) -> dict:
    if cache_path is None:
        cache_path = str(Path(__file__).resolve().parents[2] / "semantic_cache.json")

    p = Path(cache_path)
    if not p.exists():
        raise FileNotFoundError(f"semantic_cache.json not found at: {p}")

    return json.loads(p.read_text(encoding="utf-8"))


def build_llm_schema_text(cache: dict) -> str:
    """
    Converts your mapping json into schema string for Groq Cypher generator.
    """

    tables = cache.get("tables", {})
    columns = cache.get("columns", {})
    rels = cache.get("relationships", {})

    lines = []
    lines.append("NODES (Neo4j Labels):")
    for table, label in tables.items():
        lines.append(f"- {label}  (source_table={table})")

    lines.append("\nPROPERTIES (Neo4j Node Properties):")
    for col, prop in columns.items():
        lines.append(f"- {prop}  (source_column={col})")

    lines.append("\nRELATIONSHIPS (Neo4j Relationship Types):")
    for k, reltype in rels.items():
        child, parent = k.split("->")
        child_label = tables.get(child, child)
        parent_label = tables.get(parent, parent)
        lines.append(f"- ({child_label})-[:{reltype}]-({parent_label})")

    lines.append("\nIMPORTANT RULES:")
    lines.append("- Use ONLY these labels, properties, and relationship types")
    lines.append("- Use READ-ONLY Cypher only")
    lines.append("- Always include RETURN")

    return "\n".join(lines)
