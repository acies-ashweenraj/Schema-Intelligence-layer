import os
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

    result = run_hybrid_mapping(
        src_cfg=src_cfg,
        tgt_cfg=tgt_cfg,
        qdrant_host=payload.qdrant_host,
        qdrant_port=payload.qdrant_port,
        groq_cfg=GroqConfig(api_key=groq_key),
        top_k_dense=payload.top_k_dense,
    )

    return result
