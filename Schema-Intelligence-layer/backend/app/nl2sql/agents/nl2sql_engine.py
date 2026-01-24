import json
import logging
import os
import pickle
import re
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

import networkx as nx
import pandas as pd
from dotenv import load_dotenv
from groq import Groq
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.core.tracker import QueryMetricsTracker


# ============================================================================
# CONFIGURATION & LOGGING
# ============================================================================

load_dotenv()

logger = logging.getLogger("NL2SQLEngine")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# ============================================================================
# NL2SQL ENGINE CLASS
# ============================================================================

class NL2SQLRunner:
    """
    Orchestrates NL→SQL conversion using LLM + knowledge graph.
    """

    def __init__(
        self,
        client_id: str,
        graph_path: Path,
        engine: Engine,
        groq_api_key: Optional[str] = None,
        model: str = os.getenv("GROQ_MODEL", "meta-llama/llama-4-maverick-17b-128e-instruct"),
    ):
        """
        Initialize NL2SQL runner.

        Args:
            client_id: Database/client identifier (e.g., "c1ehs_oilgas", "C2_CONSTRUCTION")
            graph_path: Path to knowledge_graph_enhanced.gpickle
            engine: SQLAlchemy database engine
            groq_api_key: Groq API key (reads from env if not provided)
            model: Groq model ID
        """
        self.client_id = client_id
        self.graph_path = graph_path
        self.db_engine = engine
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.query_tracker = QueryMetricsTracker() # Instantiate QueryMetricsTracker

        self.graph: Optional[nx.DiGraph] = None
        self.groq_client: Optional[Groq] = None

        logger.info(f"✅ NL2SQLRunner initialized for client: {client_id}")
    def initialize(self) -> None:
        """Load all resources (graph, LLM)."""
        logger.info("\n" + "=" * 70)
        logger.info("INITIALIZING NL2SQL ENGINE")
        logger.info("=" * 70)

        # Load graph
        logger.info("\n1️⃣  Loading knowledge graph...")
        self._load_graph()

        # Initialize Groq client
        logger.info("\n2️⃣  Initializing Groq LLM...")
        self._init_groq()

        logger.info("\n✅ NL2SQL Engine ready!\n")
    
    def _load_graph(self) -> None:
        """Load NetworkX knowledge graph."""
        if not self.graph_path.exists():
            raise FileNotFoundError(f"Knowledge graph not found: {self.graph_path}")

        with open(self.graph_path, "rb") as f:
            self.graph = pickle.load(f)
        logger.info(f"   🔗 {self.graph.number_of_nodes()} nodes")
        logger.info(f"   🔀 {self.graph.number_of_edges()} edges")
        logger.info(f"   ✅ Loaded from: {self.graph_path.name}")

    def _init_groq(self) -> None:
        """Initialize Groq API client."""
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not set in environment")

        self.groq_client = Groq(api_key=self.groq_api_key)
        logger.info(f"   🤖 Model: {self.model}")
        logger.info(f"   ✅ Groq API ready")



    # ======================================================================== 
    # SCHEMA CONTEXT BUILDING
    # ======================================================================== 

    def _build_schema_context(self, max_cols_per_table: int = 20) -> str:
        """
        Build compact schema context from the knowledge graph for the LLM prompt.

        Args:
            max_cols_per_table: Limit columns per table to avoid token bloat

        Returns:
            Human-readable schema string
        """
        if not self.graph:
            return "No graph loaded."

        lines: List[str] = []
        table_nodes = [
            (n, d)
            for n, d in self.graph.nodes(data=True)
            if d.get("node_type") == "table"
        ]

        for table_name, table_data in table_nodes:
            # Extract column info from the graph
            column_nodes = [
                (n, d)
                for n, d in self.graph.nodes(data=True)
                if d.get("node_type") == "column" and n.startswith(f"{table_name}:")
            ]
            
            col_specs = [
                f"{d.get('column_name')} ({d.get('data_type', 'UNKNOWN')})"
                for n, d in column_nodes
            ]

            # Extract relationship info from graph edges
            relationships = self.graph.out_edges(table_name, data=True)
            rel_specs = [
                f"{edge[1]}.{d.get('target_column', 'id')}"
                for edge in relationships if (d := edge[2]) and d.get("relation_type") == "foreign_key"
            ]

            line = f"TABLE {table_name}:\n"
            line += f"  Columns: {', '.join(col_specs[:max_cols_per_table])}"
            if len(col_specs) > max_cols_per_table:
                line += f" ... +{len(col_specs) - max_cols_per_table} more"
            line += "\n"

            if rel_specs:
                line += f"  Joins: {', '.join(rel_specs)}\n"

            lines.append(line)

        return "\n".join(lines)

    # ======================================================================== 
    # QUESTION → SQL CONVERSION
    # ======================================================================== 

    def question_to_sql(self, question: str) -> str:
        """
        Convert natural language question to SQL.

        Args:
            question: Natural language query

        Returns:
            SQL SELECT statement
        """
        if not self.groq_client:
            raise RuntimeError("Engine not initialized. Call initialize() first.")

        logger.info(f"\n❓ Question: {question}")
        logger.info("⚡ Generating SQL...")

        start_time = time.time()

        # Build schema context
        schema_context = self._build_schema_context()
        print(f"Schema Context:\n{schema_context}")

        # Build prompt
        system_prompt = """You are an expert PostgreSQL analyst for an EHS (Environmental, Health & Safety) database.

You have been provided with a PRECOMPUTED SCHEMA CONTEXT that lists exactly which tables, columns, and joins exist.

Rules:
1. Use ONLY the tables and columns shown in the schema context.
2. DO NOT query the information_schema. Use the provided context to answer questions about the schema.
3. Never invent table or column names.
4. Use real business logic from the context (joins, relationships).
5. Return ONLY raw SQL (no explanations, no markdown, no backticks).
6. End with a semicolon.
7. Use lowercase for keywords (SELECT, FROM, WHERE, JOIN).
8. Use INNER JOIN or LEFT JOIN as appropriate.
"""

        user_prompt = f"""SCHEMA CONTEXT FOR {self.client_id}:
{schema_context}

TASK: Write a PostgreSQL SELECT query to answer this question:
"{question}"

Return ONLY the SQL statement, nothing else."""

        sql = ""
        success = False
        error_message = None
        input_tokens = 0
        output_tokens = 0
        
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
                max_tokens=1000,
                timeout=30,
            )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            sql = response.choices[0].message.content.strip()
            sql = self._clean_sql(sql)
            
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            
            elapsed = end_time - start_time
            logger.info(f"✅ SQL generated ({elapsed:.2f}s)")
            logger.info(f"📝 SQL:\n{sql}\n")
            
            success = True
            confidence = 1.0 # Placeholder, could be improved with SQL validation
            
            return sql

        except Exception as e:
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            error_message = str(e)
            logger.error(f"❌ LLM error: {error_message}")
            confidence = 0.0 # No confidence on error
            return ""
        finally:
            self.query_tracker.log_query(
                nl_query=question,
                sql_query=sql,
                success=success,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
                confidence=confidence if success else 0.0,
                error=error_message,
                table_count=0, # Placeholder, can be improved
                complexity="unknown" # Placeholder, can be improved
            )

    def _clean_sql(self, sql: str) -> str:
        """Remove markdown artifacts and normalize SQL."""
        if not sql:
            return ""

        # Remove code fences
        sql = re.sub(r"```.*?\n", "", sql)
        sql = re.sub(r"```", "", sql)

        # Remove leading/trailing whitespace
        sql = sql.strip()

        # Ensure semicolon
        if not sql.endswith(";"):
            sql += ";"

        return sql

    # ======================================================================== 
    # SQL EXECUTION
    # ======================================================================== 

    def execute_sql(self, sql: str, client_id: Optional[str] = None) -> Union[pd.DataFrame, str]:
        """
        Execute SQL and return results.

        Args:
            sql: SQL statement
            client_id: Optional override for database selection

        Returns:
            Pandas DataFrame or error message
        """
        if not self.db_engine:
            return "❌ Database engine not initialized"

        client_id = client_id or self.client_id

        # Safety check: block dangerous operations
        dangerous = ["drop", "delete", "truncate", "alter", "update", "create", "insert"]
        if any(kw in sql.lower() for kw in dangerous):
            return "🚫 Safety Alert: Destructive operations are blocked"

        try:
            logger.info(f"⚡ Executing on {client_id}...")
            start = time.time()

            with self.db_engine.connect() as conn:
                df = pd.read_sql(text(sql), conn)

            elapsed = time.time() - start
            logger.info(f"✅ Executed ({elapsed:.2f}s, {len(df)} rows)")

            return df

        except SQLAlchemyError as e:
            error_msg = f"❌ Database error: {str(e)[:200]}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"❌ Execution error: {str(e)[:200]}"
            logger.error(error_msg)
            return error_msg


# ============================================================================ 
# STANDALONE EXECUTION (for testing)
# ============================================================================ 

def run_interactive_session(client_id: str):
    """
    Run interactive NL2SQL session.

    Args:
        client_id: Client identifier (e.g., "c1ehs_oilgas")
    """
    client_dir = Config._client_config.client_artifacts_dir
    graph_path = client_dir / "knowledge_graph_enhanced.gpickle"

    if not graph_path.exists():
        print(f"❌ Knowledge graph not found: {graph_path}")
        print("Run the full pipeline (main.py) first to generate the graph.")
        return

    print("\n" + "=" * 70)
    print("🚀 NL2SQL INTERACTIVE SESSION")
    print("=" * 70)

    runner = NL2SQLRunner(
        client_id=client_id,
        graph_path=graph_path,
        engine=Config.get_engine(),
    )
    runner.initialize()

    # Interactive loop
    print("\n" + "-" * 70)
    print("💡 Type your questions (or 'quit' to exit)\n")

    while True:
        try:
            question = input("❓ Your question: ").strip()

            if question.lower() in {"quit", "exit", "q"}:
                print("👋 Goodbye!")
                break

            if not question:
                continue

            sql = runner.question_to_sql(question)

            if sql and runner.db_engine:
                result = runner.execute_sql(sql)

                if isinstance(result, pd.DataFrame):
                    print(f"\n📊 Results ({len(result)} rows):")
                    print(result.head(10).to_string(index=False))
                else:
                    print(f"\n{result}")

            print("-" * 70)

        except KeyboardInterrupt:
            print("\n👋 Session interrupted")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        finally:
            runner.query_tracker.print_summary() # Print summary on exit or error
            runner.query_tracker.export_to_json() # Export data to JSON


if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    from app.core.config import Config

    load_dotenv() # Load environment variables

    # Prompt user for client ID or use a default
    client_id = input("Enter client ID (e.g., c1ehs_oilgas or C2_CONSTRUCTION) for NL2SQL Engine: ").strip()
    if not client_id:
        client_id = "c1ehs_oilgas" # Default for standalone execution
        print(f"No client ID provided, using default: {client_id}")

    try:
        Config.set_client_id(client_id)
        run_interactive_session(client_id)
    except Exception as e:
        print(f"Error during standalone execution of NL2SQL Engine: {e}")
        sys.exit(1)