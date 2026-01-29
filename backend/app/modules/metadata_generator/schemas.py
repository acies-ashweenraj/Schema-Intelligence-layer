from pydantic import BaseModel, Field
from typing import Literal


class MetadataRequest(BaseModel):
    db_type: str
    host: str
    port: int
    database: str
    username: str
    password: str
    schema_name: str
    output_format: Literal["csv", "json", "xlsx"]
