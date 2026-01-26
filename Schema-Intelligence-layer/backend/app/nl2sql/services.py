import os
import json
import pandas as pd
from typing import Dict, Any, Optional, List,Union
from pathlib import Path
from functools import lru_cache

# Import project-specific modules
from app.core.config import Config
from app.nl2sql.agents.graph_store_neo4j import (
    Neo4jGraphStore,
    Neo4jConfig,
)
from app.nl2sql.agents.nl2sql_chat_agent import NL2SQLChatAgent
# from src.nl2sql.nl2sql_from_neo4j import NL2SQLFromNeo4jRunner
from app.nl2sql.agents.nl2sql_engine import NL2SQLRunner
from app.core.tracker import QueryMetricsTracker

# Import Pydantic models for API communication
from .models import ChatRequest, ChatResponse, ChatMessage

# --- Global Cache for Agent Instances ---
# Using functools.lru_cache to cache agents based on their initialization parameters.
# This prevents re-initializing expensive agents on every API request.
# The cache size is set to 3 to keep agents for all 3 types if they are used concurrently.
@lru_cache(maxsize=3)
def get_agent_instance(client_id: str, agent_name: str, model_name: str) -> Union[NL2SQLChatAgent, NL2SQLRunner]:
    """
    Dynamically imports and returns an initialized agent instance.
    The agent instance is cached based on client_id, agent_name, and model_name.
    """
    # Ensure client configuration is set for the current context
    Config.set_client_id(client_id)
    db_engine = Config.get_engine()

    # Determine if Neo4j store is needed
    neo4j_store = None
    if "Neo4j" in agent_name or "Conversational" in agent_name:
        neo4j_config = Neo4jConfig(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD"),
            database="neo4j",
        )
        neo4j_store = Neo4jGraphStore(neo4j_config)

    # Initialize the specific agent
    if agent_name == "Conversational Agent":
        agent = NL2SQLChatAgent(
            client_id=client_id,
            neo4j_store=neo4j_store,
            db_engine=db_engine,
            model=model_name
        )
    elif agent_name == "Neo4j Engine":
        raise ValueError("The 'Neo4j Engine' is not currently supported. This functionality is either under development or has been superseded.")
    # elif agent_name == "Neo4j Engine":
    #     agent = NL2SQLFromNeo4jRunner(
    #         client_id=client_id,
    #         neo4j_store=neo4j_store,
    #         db_engine=db_engine,
    #         model=model_name
    #     )
    elif agent_name == "NetworkX Engine":
        # Point to the static graph file located in the 'agents' subdirectory.
        graph_path = Path(__file__).parent / "agents" / "knowledge_graph_enhanced.gpickle"
        if not graph_path.exists():
            raise FileNotFoundError(f"Knowledge graph not found at expected path: {graph_path}")

        agent = NL2SQLRunner(
            client_id=client_id,
            graph_path=graph_path,
            engine=db_engine,
            model=model_name
        )
        agent.initialize() # NetworkX Engine has an explicit initialize method
    else:
        raise ValueError(f"Unknown agent: {agent_name}")
            
    return agent


async def process_chat_message(request: ChatRequest) -> ChatResponse:
    """
    Processes a user's chat message using the selected AI agent.
    Returns a structured ChatResponse.
    """
    try:
        agent = get_agent_instance(request.client_id, request.agent_name, request.model_name)

        if request.agent_name == "Conversational Agent":
            # BUG FIX: The agent is cached, but its internal history must be rebuilt for each stateless request.
            # 1. Get the system prompt, which is always the first item in the cached agent's history.
            system_prompt_message = agent.full_history[0]
            
            # 2. Reconstruct the history for this specific request.
            # Start with the system prompt, then add the history from the client.
            request_history = [msg.dict() for msg in request.history]
            agent.current_history = [system_prompt_message] + request_history
            agent.full_history = [system_prompt_message] + request_history

            # 3. Call the agent's method with the new user message.
            # The agent will append this message to its histories internally.
            raw_ai_response = agent.get_llm_response({"role": "user", "content": request.user_message})
            parsed_response = json.loads(raw_ai_response)

            # Fix: Provide a default for 'mode' and update it based on context.
            mode = parsed_response.get("mode", "summary_only") # Default to summary_only
            summary = parsed_response.get("summary")
            sql = parsed_response.get("sql")
            dataframe_data: Optional[Dict[str, Any]] = None
            error_message: Optional[str] = None

            if sql:
                # If SQL is present, the mode should reflect that.
                if mode == "summary_only":
                    mode = "sql_and_summary" 

                db_result = agent.execute_sql(sql)
                if isinstance(db_result, pd.DataFrame):
                    dataframe_data = db_result.to_dict(orient="records")
                    if mode == "sql_and_summary":
                        final_summary = agent.generate_final_summary(
                            request.user_message, summary, db_result
                        )
                        summary = final_summary
                else:
                    error_message = db_result
                    mode = "summary_only"
                    summary = f"I generated the SQL but it failed to execute: {error_message}"
        
        elif request.agent_name in ["Neo4j Engine", "NetworkX Engine"]:
            sql_query = agent.question_to_sql(request.user_message)
            dataframe_data = None
            error_message = None
            summary = "Generated SQL"
            mode = "sql_only"

            if sql_query:
                db_result = agent.execute_sql(sql_query)
                if isinstance(db_result, pd.DataFrame):
                    dataframe_data = db_result.to_dict(orient="records")
                    summary = f"Successfully executed query. Found {len(db_result)} rows."
                else:
                    error_message = db_result
                    summary = f"SQL generated but failed to execute: {error_message}"
                    sql_query = None

            return ChatResponse(
                mode=mode,
                summary=summary,
                sql=sql_query,
                dataframe=dataframe_data,
                error=error_message
            )
        else:
            raise ValueError(f"Unknown agent: {request.agent_name}")

        return ChatResponse(
            mode=mode,
            summary=summary,
            sql=sql,
            dataframe=dataframe_data,
            error=error_message
        )
    except Exception as e:
        return ChatResponse(
            mode="summary_only",
            summary=f"An unexpected error occurred during processing: {e}",
            error=str(e)
        )
    
    
    def get_query_metrics() -> Dict[str, Any]:
        """
        Loads query metrics from the log file and returns a summary.
        """
        try:
            tracker = QueryMetricsTracker()
            tracker.load_existing_queries()
            return tracker.get_summary()
        except Exception as e:
            # Log the error and return a friendly message
            # In a real app, you'd use a proper logger
            print(f"Error loading metrics: {e}")
            return {
                "error": "Could not load metrics data.",
                "details": str(e)
            }    