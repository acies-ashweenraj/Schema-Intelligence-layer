from pydantic import BaseModel


class AskRequest(BaseModel):
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    neo4j_database: str = "neo4j"
    question: str
