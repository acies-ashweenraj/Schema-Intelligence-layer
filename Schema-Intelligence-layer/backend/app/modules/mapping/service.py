import os
from pathlib import Path # Add this import
from typing import Optional # Add this import
from schema_matching_toolkit import DBConfig, GroqConfig
from schema_matching_toolkit.hybrid_ensemble_matcher import run_hybrid_mapping


def run_hybrid_mapping_service(payload, output_dir: Optional[str] = None):
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise ValueError("GROQ_API_KEY not found in .env")

    # Define default output directory
    BASE_DIR = Path(__file__).resolve().parent.parent.parent # Schema-Intelligence-layer/backend
    DEFAULT_LOGS_DIR = BASE_DIR / "logs"
    final_output_dir = output_dir if output_dir else str(DEFAULT_LOGS_DIR)

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

    original_cwd = os.getcwd()
    try:
        os.makedirs(final_output_dir, exist_ok=True)
        os.chdir(final_output_dir)

        result = run_hybrid_mapping(
            src_cfg=src_cfg,
            tgt_cfg=tgt_cfg,
            qdrant_host=payload.qdrant_host,
            qdrant_port=payload.qdrant_port,
            groq_cfg=GroqConfig(api_key=groq_key),
            top_k_dense=payload.top_k_dense,
        )
    finally:
        os.chdir(original_cwd)

    # Reconstruct the full path for the saved file
    saved_file = result.get("saved_file")
    if saved_file:
        full_saved_path = os.path.join(final_output_dir, saved_file)
        result['saved_file'] = full_saved_path # Update the result dict

    return result
