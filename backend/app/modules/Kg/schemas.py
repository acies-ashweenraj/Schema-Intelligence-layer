from pydantic import BaseModel, Field


class PostgresConfig(BaseModel):
    host: str = Field(..., example="localhost")
    port: int = Field(default=5432, example=5432)
    database: str = Field(..., example="employee")
    username: str = Field(..., example="postgres")
    password: str = Field(..., example="your_password")
    schema_name: str = Field(default="public", example="public")


class Neo4jConfig(BaseModel):
    uri: str = Field(..., example="bolt://localhost:7687")
    user: str = Field(..., example="neo4j")
    password: str = Field(..., example="your_password")


class KGLoadRequest(BaseModel):
    pg: PostgresConfig
    neo4j: Neo4jConfig
