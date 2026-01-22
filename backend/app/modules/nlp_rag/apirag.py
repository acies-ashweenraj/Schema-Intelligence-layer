from fastapi import FastAPI
from contextlib import asynccontextmanager
from graph_rag import GraphRAG
import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE="neo4j"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

rag = None  # global placeholder

@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag
    # Initialize GraphRAG safely during startup
    rag = GraphRAG(
        neo4j_url=NEO4J_URI,
        neo4j_user=NEO4J_USER,
        neo4j_password=NEO4J_PASSWORD,
        neo4j_database=NEO4J_DATABASE,
        api_key=GROQ_API_KEY
    )
    yield
    # Optional cleanup code on shutdown
    rag = None

app = FastAPI(lifespan=lifespan)

# Pydantic model for POST request
from pydantic import BaseModel

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask(q: Question):
    result = rag.ask(q.question)
    return {"question": q.question, "result": result}

# Optional: simple health check
@app.get("/ping")
def ping():
    return {"status": "ok"}

# uvicorn api_rag:app --reload
# http://localhost:8000/docs
# uvicorn api_rag:app --reload --host 0.0.0.0 --port 8000