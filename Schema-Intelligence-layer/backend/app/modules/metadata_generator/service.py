import os
from pathlib import Path # Add this import
from typing import Optional # Add this import
from schema_matching_toolkit import DBConfig, GroqConfig
from schema_matching_toolkit.schema_metadata_generator import generate_schema_metadata


def run_metadata_generation(payload, output_dir: Optional[str] = None):
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise ValueError("GROQ_API_KEY not found in environment (.env)")

    # Define default output directory
    BASE_DIR = Path(__file__).resolve().parent.parent.parent # Schema-Intelligence-layer/backend
    DEFAULT_LOGS_DIR = BASE_DIR / "logs"
    final_output_dir = output_dir if output_dir else str(DEFAULT_LOGS_DIR)

    db_cfg = DBConfig(
        db_type=payload.db_type,
        host=payload.host,
        port=payload.port,
        database=payload.database,
        username=payload.username,
        password=payload.password,
        schema_name=payload.schema_name,
    )

    original_cwd = os.getcwd()
    try:
        os.makedirs(final_output_dir, exist_ok=True)
        os.chdir(final_output_dir)

        # Generate metadata (heavy response)
        result = generate_schema_metadata(
            db_cfg=db_cfg,
            groq_cfg=GroqConfig(api_key=groq_key),
            output_format=payload.output_format,
        )
    finally:
        # Always change back to the original directory
        os.chdir(original_cwd)

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

    # Reconstruct the full path for the saved file
    saved_file = result.get("saved_file")
    full_saved_path = None
    if saved_file:
        full_saved_path = os.path.join(final_output_dir, saved_file)

    # Download URL (frontend uses this)
    download_url = None
    if full_saved_path:
        app_base_url = os.getenv("APP_BASE_URL", "http://localhost:8000")
        download_url = f"{app_base_url}/metadata/download?path={full_saved_path}"

    # ----------------------------
    # ✅ Return CLEAN response
    # ----------------------------
    return {
        "generated_at": result.get("generated_at"),
        "database": result.get("database"),
        "summary": result.get("summary"),
        "tables_preview": tables_preview,
        "columns_preview": columns_preview,
        "saved_file": full_saved_path, # Return the full path
        "download_url": download_url,
    }
