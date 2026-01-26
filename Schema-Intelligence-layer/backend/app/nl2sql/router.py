from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse # Import FileResponse
from typing import List
import os
from pathlib import Path # Import Path

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
# GET /nl2sql/download-metrics
# -------------------------------------------------
@router.get("/download-metrics")
def download_metrics_file(): # Renamed to avoid confusion with the old /metrics
    """
    Provides the query metrics summary file for download.
    """
    try:
        # Define the path to the metrics file relative to the backend's root
        metrics_file_path = Path("artifacts/query_logs/query_summary.json")

        if not metrics_file_path.exists():
            # If the file doesn't exist, it means no queries have been logged.
            raise HTTPException(status_code=404, detail="Metrics summary file not found. Please run a query first.")

        return FileResponse(
            path=metrics_file_path,
            filename="query_metrics_summary.json",
            media_type="application/json"
        )
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
