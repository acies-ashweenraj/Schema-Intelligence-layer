from pydantic import BaseModel, Field
from typing import Literal


class MetadataRequest(BaseModel):
    db_type: Literal["postgres"] = "postgres"
    host: str = Field(..., examples=["localhost"])
    port: int = Field(5433, examples=[5433])
    database: str = Field(..., examples=["ehs_client"])
    username: str = Field(..., examples=["postgres"])
    password: str = Field(..., examples=["your_password"])
    schema_name: str = Field("public", examples=["public"])

    output_format: Literal["csv", "json", "xlsx"] = "csv"
