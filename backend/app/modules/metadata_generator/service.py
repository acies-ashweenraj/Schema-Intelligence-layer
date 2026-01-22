import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from schema_matching_toolkit import DBConfig, GroqConfig
from schema_matching_toolkit.schema_metadata_generator import generate_schema_metadata


def run_metadata_generation(payload):
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise ValueError("GROQ_API_KEY not found in environment (.env)")

    # Create db config
    db_cfg = DBConfig(
        db_type=payload.db_type,
        host=payload.host,
        port=payload.port,
        database=payload.database,
        username=payload.username,
        password=payload.password,
        schema_name=payload.schema_name,
    )

    # ---- IMPORTANT FIX ----
    # Force SQLAlchemy to use AUTOCOMMIT so a failed query doesn't abort the session
    db_url = (
        f"postgresql+psycopg2://{payload.username}:{payload.password}"
        f"@{payload.host}:{payload.port}/{payload.database}"
    )

    engine: Engine = create_engine(
        db_url,
        isolation_level="AUTOCOMMIT",   # ✅ KEY FIX
        pool_pre_ping=True
    )

    result = generate_schema_metadata(
        db_cfg=db_cfg,
        groq_cfg=GroqConfig(api_key=groq_key),
        output_format=payload.output_format,
    )

    return result
