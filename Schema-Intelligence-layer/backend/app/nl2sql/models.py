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
    dataframe: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

class ConfigOptions(BaseModel):
    """Response model for the /config endpoint."""
    client_ids: List[str]
    agent_types: List[str]
    model_names: List[str]

class TotalTokens(BaseModel):
    """Represents the total input and output tokens."""
    input: int
    output: int

class MetricsSummary(BaseModel):
    """Response model for the /metrics endpoint."""
    total_queries: int
    successful: int
    failed: int
    success_rate: float
    total_tokens: TotalTokens
    total_cost_usd: float
    avg_latency_ms: float
    avg_confidence: float
    queries_needing_retry: int
    avg_retries: float
    last_updated: str
