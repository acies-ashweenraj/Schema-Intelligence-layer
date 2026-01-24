from pydantic import BaseModel, Field


class DBRequestConfig(BaseModel):
    db_type: str = Field(default="postgres", example="postgres")
    host: str = Field(..., example="localhost")
    port: int = Field(default=5432, example=5432)
    database: str = Field(..., example="employee")
    username: str = Field(..., example="postgres")
    password: str = Field(..., example="your_password")
    schema_name: str = Field(default="public", example="public")


class HybridMappingRequest(BaseModel):
    src_cfg: DBRequestConfig
    tgt_cfg: DBRequestConfig

    qdrant_host: str = Field(default="localhost", example="localhost")
    qdrant_port: int = Field(default=6333, example=6333)

    top_k_dense: int = Field(default=5, example=5)
