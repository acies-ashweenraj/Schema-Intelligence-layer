from fastapi import APIRouter, HTTPException
from typing import List
import os

from .models import ChatRequest, ChatResponse, ConfigOptions, MetricsSummary
from . import services
from app.core.paths import CONFIG_DIR

router = APIRouter(
    prefix="/nl2sql",
    tags=["NL2SQL"]
)

# -------------------------------------------------
# GET /nl2sql/config
# -------------------------------------------------
@router.get("/config", response_model=ConfigOptions)
def get_config_options():
    """
    Provides configuration options for frontend dropdowns.
    """
    client_ids = []

    # Read available client configs dynamically
    if os.path.exists(CONFIG_DIR):
        for file in os.listdir(CONFIG_DIR):
            if file.endswith(".yaml"):
                client_ids.append(os.path.splitext(file)[0])

    model_names = [
        os.getenv("GROQ_MODEL", "meta-llama/llama-4-maverick-17b-128e-instruct"),
        "llama-3.3-70b-versatile",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "qwen/qwen3-32b",
        "openai/gpt-oss-120b"
    ]

    # remove duplicates & sort
    model_names = sorted(list(set(model_names)))

    return ConfigOptions(
        client_ids=client_ids,
        agent_types=[
            "Conversational Agent",
            "Neo4j Engine",
            "NetworkX Engine"
        ],
        model_names=model_names
    )

# -------------------------------------------------
# GET /nl2sql/metrics
# -------------------------------------------------
@router.get("/metrics", response_model=MetricsSummary)
def get_metrics():
    """
    Provides a summary of query metrics from the tracker.
    """
    try:
        summary = services.get_query_metrics()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------
# POST /nl2sql/chat
# -------------------------------------------------
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main conversational NL2SQL endpoint.
    """
    try:
        response = await services.process_chat_message(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
