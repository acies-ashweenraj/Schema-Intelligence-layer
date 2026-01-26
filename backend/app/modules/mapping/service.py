import os
import pandas as pd
from datetime import datetime

from schema_matching_toolkit import DBConfig, GroqConfig
from schema_matching_toolkit.hybrid_ensemble_matcher import run_hybrid_mapping


def run_hybrid_mapping_service(payload):
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise ValueError("GROQ_API_KEY not found in .env")

    src_cfg = DBConfig(
        db_type=payload.src_cfg.db_type,
        host=payload.src_cfg.host,
        port=payload.src_cfg.port,
        database=payload.src_cfg.database,
        username=payload.src_cfg.username,
        password=payload.src_cfg.password,
        schema_name=payload.src_cfg.schema_name,
    )

    tgt_cfg = DBConfig(
        db_type=payload.tgt_cfg.db_type,
        host=payload.tgt_cfg.host,
        port=payload.tgt_cfg.port,
        database=payload.tgt_cfg.database,
        username=payload.tgt_cfg.username,
        password=payload.tgt_cfg.password,
        schema_name=payload.tgt_cfg.schema_name,
    )

    # toolkit returns mapping output (often CSV file path / dict / dataframe)
    result = run_hybrid_mapping(
        src_cfg=src_cfg,
        tgt_cfg=tgt_cfg,
        qdrant_host=payload.qdrant_host,
        qdrant_port=payload.qdrant_port,
        groq_cfg=GroqConfig(api_key=groq_key),
        top_k_dense=payload.top_k_dense,
    )

    generated_at = datetime.utcnow().isoformat()

    saved_file = None
    df = None

    # -----------------------------
    # Normalize toolkit output
    # -----------------------------
    if isinstance(result, str):
        # case: returns file path
        saved_file = result

    elif isinstance(result, dict):
        # case: returns dict
        saved_file = (
            result.get("saved_file")
            or result.get("path")
            or result.get("file")
        )

        # sometimes dict may contain rows directly
        if "data" in result and isinstance(result["data"], list):
            df = pd.DataFrame(result["data"])

    elif hasattr(result, "to_csv"):
        # case: returns pandas dataframe
        df = result
        saved_file = "mapping_output.csv"
        df.to_csv(saved_file, index=False)

    # -----------------------------
    # If saved_file exists, read it
    # -----------------------------
    preview_rows = []
    preview_csv = None

    if saved_file and os.path.exists(saved_file):
        df = pd.read_csv(saved_file)

    if df is not None and not df.empty:
        preview_rows = df.head(15).to_dict(orient="records")
        preview_csv = df.head(15).to_csv(index=False)

    # -----------------------------
    # Dashboard summary
    # -----------------------------
    table_match_count = 0
    column_match_count = 0
    avg_table_conf = None
    avg_col_conf = None

    if df is not None and not df.empty:
        # table matches = unique source_table -> target_table pairs
        if "source_table" in df.columns and "target_table" in df.columns:
            table_match_count = int(df[["source_table", "target_table"]].drop_duplicates().shape[0])

        # column matches = total rows
        column_match_count = int(len(df))

        if "table_confidence" in df.columns:
            avg_table_conf = float(df["table_confidence"].mean())

        if "column_confidence" in df.columns:
            avg_col_conf = float(df["column_confidence"].mean())

    return {
        "status": "success",
        "generated_at": generated_at,
        "saved_file": saved_file,

        # counts for UI dashboard
        "table_match_count": table_match_count,
        "column_match_count": column_match_count,
        "avg_table_confidence": avg_table_conf,
        "avg_column_confidence": avg_col_conf,

        # preview for UI
        "preview_rows": preview_rows,
        "preview_csv": preview_csv,
    }
