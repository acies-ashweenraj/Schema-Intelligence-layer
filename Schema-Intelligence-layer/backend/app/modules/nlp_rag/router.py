from fastapi import APIRouter
from pydantic import BaseModel
from .service import ask_question

router = APIRouter(prefix="/nlp-rag", tags=["NLP-RAG"])


class Question(BaseModel):
    question: str


@router.post("/ask")
def ask(q: Question):
    return ask_question(q.question)


