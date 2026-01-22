import os
from dotenv import load_dotenv
from .graph_rag import GraphRAG

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = "neo4j"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

rag = None


def get_rag():
    global rag
    if rag is None:
        rag = GraphRAG(
            neo4j_url=NEO4J_URI,
            neo4j_user=NEO4J_USER,
            neo4j_password=NEO4J_PASSWORD,
            neo4j_database=NEO4J_DATABASE,
            api_key=GROQ_API_KEY
        )
    return rag


def ask_question(question: str):
    rag_instance = get_rag()
    result = rag_instance.ask(question)
    return {"question": question, "result": result}
