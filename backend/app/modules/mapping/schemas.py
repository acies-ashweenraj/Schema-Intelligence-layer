from pydantic import BaseModel
from typing import Optional


class DBConfigRequest(BaseModel):
    db_type: str
    host: str
    port: int
    database: str
    username: str
    password: str
    schema_name: str


class HybridMappingRequest(BaseModel):
    src_cfg: DBConfigRequest
    tgt_cfg: DBConfigRequest

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    top_k_dense: int = 5

    # ✅ ADD THIS
    output_format: str = "csv"  # csv | json | xlsx
    min_confidence: float = 0.5
