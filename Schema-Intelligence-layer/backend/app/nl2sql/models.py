from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ChatMessage(BaseModel):
    """Represents a single message in the conversation history."""
    role: str
    content: str

class ChatRequest(BaseModel):
    """The request body for the /chat endpoint."""
    user_message: str
    history: List[ChatMessage]
    client_id: str
    agent_name: str
    model_name: str

class ChatResponse(BaseModel):
    """The structured response from the /chat endpoint."""
    mode: str
    summary: Optional[str] = None
    sql: Optional[str] = None
    chart_suggestion: Optional[str] = None  # e.g., "bar", "line", "pie", "scatter"
    dataframe: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    full_history: Optional[List[ChatMessage]] = None

class ConfigOptions(BaseModel):
    """Response model for the /config endpoint."""
    client_ids: List[str]
    agent_types: List[str]
    model_names: List[str]
