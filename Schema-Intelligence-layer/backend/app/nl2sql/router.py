from fastapi import APIRouter, HTTPException
from typing import List
import os

from .models import ChatRequest, ChatResponse, ConfigOptions
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
        "meta-llama/llama-3-70b-instruct",
        "meta-llama/llama-3-8b-instruct",
        "mixtral-8x7b-32768",
        "gemma-7b-it"
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
