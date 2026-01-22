from fastapi import APIRouter
from pydantic import BaseModel
from .service import ask_question

router = APIRouter(prefix="/nlp", tags=["NLP"])

class AskRequest(BaseModel):
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    neo4j_database: str
    question: str

@router.post("/ask")
def ask(req: AskRequest):
    return ask_question(req)
