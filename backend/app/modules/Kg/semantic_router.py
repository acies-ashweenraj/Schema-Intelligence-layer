import os
import json
import re

from app.modules.Kg.semantic_llm import (
    llm_table_label,
    llm_column_name,
    llm_relationship_name,
)

CACHE_FILE = "semantic_cache.json"
USE_LLM = True


def set_llm_usage(value: bool):
    global USE_LLM
    USE_LLM = bool(value)


def _sanitize_property_name(name: str) -> str:
    if not name:
        return "unknownProperty"

    name = name.strip().replace('"', "").replace("'", "")
    name = re.sub(r"[\s\-]+", "_", name)
    name = re.sub(r"[^a-zA-Z0-9_]", "", name)

    if re.match(r"^[0-9]", name):
        name = "_" + name

    parts = name.split("_")
    if len(parts) > 1:
        name = parts[0].lower() + "".join(p.capitalize() for p in parts[1:])
    else:
        name = parts[0].lower()

    return name


def _sanitize_label(label: str) -> str:
    if not label:
        return "Entity"

    label = label.strip().replace('"', "").replace("'", "")
    label = re.sub(r"[^a-zA-Z0-9]", "", label)

    if not label:
        return "Entity"

    if re.match(r"^[0-9]", label):
        label = "Entity" + label

    return label


def _sanitize_relationship(rel: str) -> str:
    if not rel:
        return "RELATED_TO"

    rel = rel.strip().replace('"', "").replace("'", "")
    rel = rel.upper()
    rel = re.sub(r"[\s\-]+", "_", rel)
    rel = re.sub(r"[^A-Z0-9_]", "", rel)

    if not rel:
        return "RELATED_TO"

    if re.match(r"^[0-9]", rel):
        rel = "REL_" + rel

    return rel


def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"tables": {}, "columns": {}, "relationships": {}}
    return {"tables": {}, "columns": {}, "relationships": {}}


def save_cache(c):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(c, f, indent=2)


CACHE = load_cache()


def get_node_label(table: str, desc: str) -> str:
    if table not in CACHE["tables"]:
        raw = llm_table_label(desc) if USE_LLM else table.title()
        CACHE["tables"][table] = _sanitize_label(raw)
        save_cache(CACHE)
    return CACHE["tables"][table]


def get_property_name(col: str, desc: str) -> str:
    key = col.lower()
    if key not in CACHE["columns"]:
        raw = llm_column_name(desc) if USE_LLM else key
        CACHE["columns"][key] = _sanitize_property_name(raw)
        save_cache(CACHE)
    return CACHE["columns"][key]


def get_relationship_name(child: str, parent: str, child_desc: str, parent_desc: str) -> str:
    key = f"{child}->{parent}"
    if key not in CACHE["relationships"]:
        raw = llm_relationship_name(child_desc, parent_desc) if USE_LLM else "RELATED_TO"
        CACHE["relationships"][key] = _sanitize_relationship(raw)
        save_cache(CACHE)
    return CACHE["relationships"][key]
