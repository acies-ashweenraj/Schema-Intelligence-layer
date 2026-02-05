import os
import pandas as pd
from datetime import datetime
from pathlib import Path

from schema_matching_toolkit import DBConfig, GroqConfig
from schema_matching_toolkit.hybrid_ensemble_matcher import run_hybrid_mapping

# --------------------------------------------------
# Artifact directory
# --------------------------------------------------
ARTIFACT_DIR = Path("artifacts/mapping")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def run_hybrid_mapping_service(payload):
    # --------------------------------------------------
    # Validate GROQ key
    # --------------------------------------------------
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise RuntimeError("GROQ_API_KEY not found in environment")

    # --------------------------------------------------
    # Build DB configs
    # --------------------------------------------------
    src_cfg = DBConfig(**payload.src_cfg.dict())
    tgt_cfg = DBConfig(**payload.tgt_cfg.dict())

    # --------------------------------------------------
    # Run hybrid mapping (toolkit)
    # --------------------------------------------------
    result = run_hybrid_mapping(
        src_cfg=src_cfg,
        tgt_cfg=tgt_cfg,
        qdrant_host=payload.qdrant_host,
        qdrant_port=payload.qdrant_port,
        groq_cfg=GroqConfig(api_key=groq_key),
        top_k_dense=payload.top_k_dense,
        min_confidence=payload.min_confidence
    )

    generated_at = datetime.utcnow().isoformat()

    # --------------------------------------------------
    # Normalize toolkit output → DataFrame
    # --------------------------------------------------
    df = None
    csv_path = None

    if isinstance(result, str):
        csv_path = Path(result)

    elif isinstance(result, pd.DataFrame):
        df = result

    elif isinstance(result, dict):
        csv_path = Path(
            result.get("saved_file")
            or result.get("path")
            or result.get("file", "")
        )

    if csv_path and csv_path.exists():
        df = pd.read_csv(csv_path)

    if df is None or df.empty:
        raise RuntimeError("Mapping produced no results")

    # --------------------------------------------------
    # DASHBOARD METRICS (FINAL & COMPLETE)
    # --------------------------------------------------
    source_tables = set()
    target_tables = set()
    table_pairs = set()

    conf_sum = 0.0
    conf_count = 0

    for _, r in df.iterrows():
        src_tbl = r.get("source_table")
        tgt_tbl = r.get("target_table")

        if pd.notna(src_tbl):
            source_tables.add(src_tbl)

        if pd.notna(tgt_tbl):
            target_tables.add(tgt_tbl)

        if pd.notna(src_tbl) and pd.notna(tgt_tbl):
            table_pairs.add(f"{src_tbl}->{tgt_tbl}")

        col_conf = r.get("column_confidence")
        if pd.notna(col_conf):
            conf_sum += float(col_conf)
            conf_count += 1

    dashboard = {
        "source_tables_used": len(source_tables),
        "target_tables_used": len(target_tables),
        "matched_table_pairs": len(table_pairs),
        "matched_columns": int(len(df)),
        "avg_confidence_score": round(conf_sum / conf_count, 4) if conf_count else None,
    }

    # --------------------------------------------------
    # Preview rows for UI
    # --------------------------------------------------
    preview_rows = df.head(15).to_dict(orient="records")
    # FULL rows for UI editing
    all_rows = df.to_dict(orient="records")

    # --------------------------------------------------
    # Output format handling
    # --------------------------------------------------
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    output_format = (
        payload.output_format.lower()
        if hasattr(payload, "output_format") and payload.output_format
        else "csv"
    )

    if output_format == "csv":
        output_file = ARTIFACT_DIR / f"mapping_{timestamp}.csv"
        df.to_csv(output_file, index=False)

    elif output_format == "json":
        output_file = ARTIFACT_DIR / f"mapping_{timestamp}.json"
        df.to_json(output_file, orient="records", indent=2)

    elif output_format == "xlsx":
        output_file = ARTIFACT_DIR / f"mapping_{timestamp}.xlsx"
        df.to_excel(output_file, index=False)

    else:
        raise RuntimeError(f"Unsupported output format: {output_format}")

    # --------------------------------------------------
    # FINAL API RESPONSE (Frontend-safe)
    # --------------------------------------------------
    print("ALL ROWS COUNT:", len(all_rows))
    print("DASHBOARD:", dashboard)

    return {
        "status": "success",
        "generated_at": generated_at,
        "saved_file": str(output_file),

        "details": {
            "dashboard": {
                "source_tables": len(source_tables),
                "target_tables": len(target_tables),
                "matched_tables": len(table_pairs),
                "matched_columns": int(len(df)),
                "avg_confidence_score": round(conf_sum / conf_count, 4)
                if conf_count else None,
            },

            "preview_rows": preview_rows,

            # 🔥 THIS IS WHAT YOUR UI NEEDS
            "all_rows": all_rows,
        },
    }


