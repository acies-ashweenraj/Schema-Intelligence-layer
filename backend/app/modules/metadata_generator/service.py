import os
from schema_matching_toolkit import DBConfig, GroqConfig
from schema_matching_toolkit.schema_metadata_generator import generate_schema_metadata


def run_metadata_generation(payload):
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise ValueError("GROQ_API_KEY not found in environment (.env)")

    # Build DBConfig
    db_cfg = DBConfig(
        db_type=payload.db_type,
        host=payload.host,
        port=payload.port,
        database=payload.database,
        username=payload.username,
        password=payload.password,
        schema_name=payload.schema_name,
    )

    # Generate metadata (heavy response)
    result = generate_schema_metadata(
        db_cfg=db_cfg,
        groq_cfg=GroqConfig(api_key=groq_key),
        output_format=payload.output_format,
    )

    # ----------------------------
    # ✅ Build LIGHT UI PREVIEW
    # ----------------------------
    tables_preview = []
    columns_preview = []

    for t in result.get("tables", []):
        tables_preview.append(
            {
                "table_name": t.get("table_name"),
                "row_count": t.get("row_count", 0),
                "column_count": t.get("column_count", 0),
            }
        )

        # only take first few columns per table for preview
        for c in (t.get("columns") or [])[:5]:
            columns_preview.append(
                {
                    "table_name": t.get("table_name"),
                    "column_name": c.get("column_name"),
                    "data_type": c.get("data_type"),
                }
            )

    saved_file = result.get("saved_file")

    # Download URL (frontend uses this)
    download_url = None
    if saved_file:
        download_url = f"http://localhost:8000/metadata/download?path={saved_file}"

    # ----------------------------
    # ✅ Return CLEAN response
    # ----------------------------
    return {
        "generated_at": result.get("generated_at"),
        "database": result.get("database"),
        "summary": result.get("summary"),
        "tables_preview": tables_preview,
        "columns_preview": columns_preview,
        "saved_file": saved_file,
        "download_url": download_url,
    }
