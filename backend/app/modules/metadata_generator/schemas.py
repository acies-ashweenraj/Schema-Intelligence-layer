from pydantic import BaseModel


class MetadataGenerateRequest(BaseModel):
    db_type: str = "postgres"
    host: str
    port: int = 5432
    database: str
    username: str
    password: str
    schema_name: str = "public"
    output_format: str = "csv"
