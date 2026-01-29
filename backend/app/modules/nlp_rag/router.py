# from fastapi import APIRouter
# from pydantic import BaseModel
# from .service import ask_question

# router = APIRouter(prefix="/nlp-rag", tags=["NLP-RAG"])


# class Question(BaseModel):
#     question: str


# @router.post("/ask")
# def ask(q: Question):
#     return ask_question(q.question)

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

from .service import init_rag, ask_question

router = APIRouter(prefix="/nlp-rag", tags=["NLP-RAG"])


class InitRAGRequest(BaseModel):
    session_id: str
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    neo4j_database: str = "neo4j"


class Question(BaseModel):
    session_id: str
    question: str


@router.post("/init")
def init(req: InitRAGRequest):
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(status_code=500, detail="GROQ_API_KEY missing")

    init_rag(
        session_id=req.session_id,
        neo4j_uri=req.neo4j_uri,
        neo4j_user=req.neo4j_user,
        neo4j_password=req.neo4j_password,
        neo4j_database=req.neo4j_database,
        api_key=os.getenv("GROQ_API_KEY"),
    )

    return {"status": "initialized"}


@router.post("/ask")
def ask(q: Question):
    return ask_question(q.session_id, q.question)

