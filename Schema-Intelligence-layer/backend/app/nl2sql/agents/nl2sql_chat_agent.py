import json
import logging
import os
import re
import time
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from groq import Groq
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# Assuming these modules exist from the project structure
from app.nl2sql.agents.graph_store_neo4j import Neo4jGraphStore, Neo4jConfig
from app.core.tracker import QueryMetricsTracker

load_dotenv()

# --- Basic logger setup ---
logger = logging.getLogger("NL2SQLChatAgent")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class NL2SQLChatAgent:
    """
    Orchestrates a conversational NL→SQL session using a structured JSON approach.
    Manages both a short-term (token-budgeted) and long-term (full transcript) history.
    """

    def __init__(
        self,
        client_id: str,
        neo4j_store: Neo4jGraphStore,
        db_engine: Engine,
        groq_api_key: Optional[str] = None,
        model: str = os.getenv("GROQ_MODEL", "meta-llama/llama-4-maverick-17b-128e-instruct"),
        token_budget: int = 6000
    ):
        self.client_id = client_id
        self.neo4j_store = neo4j_store
        self.db_engine = db_engine
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.token_budget = token_budget
        self.query_tracker = QueryMetricsTracker()

        self.groq_client = Groq(api_key=self.groq_api_key)
        logger.info(f"🤖 Model: {self.model}")

        logger.info("Building initial schema context from Neo4j...")
        self.schema_context = self._build_schema_context()
        logger.info("✅ Schema context loaded.")
        
        system_prompt = self._create_system_prompt()
        # Two-tier history
        self.current_history = [system_prompt] # Working memory for LLM
        self.full_history = [system_prompt]    # Permanent record of the session

        logger.info(f"✅ NL2SQLChatAgent initialized for client: {self.client_id}")

    def _build_schema_context(self) -> str:
        # Same as before
        lines: List[str] = []
        with self.neo4j_store._driver.session(database=self.neo4j_store.config.database) as session:
            tables_result = session.run("MATCH (t:Table {client_id: $client_id}) RETURN t.name as name", client_id=self.client_id)
            tables = [record["name"] for record in tables_result]
        for table_name in tables:
            with self.neo4j_store._driver.session(database=self.neo4j_store.config.database) as session:
                columns_result = session.run(
                    "MATCH (c:Column {client_id: $client_id, table: $table_name}) RETURN c.name as name, c.data_type as type",
                    client_id=self.client_id, table_name=table_name
                )
                col_specs = [f"{record['name']} ({record['type']})" for record in columns_result]
            relationships = self.neo4j_store.get_fk_relationships(self.client_id, table_name)
            rel_specs = [f"{rel['to_table']}({rel['to_column']})" for rel in relationships if rel['from_table'] == table_name]
            line = f"TABLE {table_name}:\n  Columns: {', '.join(col_specs)}\n"
            if rel_specs:
                line += f"  Joins to: {', '.join(rel_specs)}\n"
            lines.append(line)
        return "\n".join(lines)

    def _create_system_prompt(self) -> Dict[str, str]:
        # Same as before
        system_content = f"""You are an advanced AI data analyst for a database with the following schema.

<schema>
{self.schema_context}
</schema>

Your task is to respond to the user's request by formulating a plan and executing it. You MUST ALWAYS respond with a single, valid JSON object, and no other text.

The JSON object has the following structure:
{{
  "mode": "one of ['summary_only', 'sql_only', 'sql_and_summary']",
  "summary": "A natural language message for the user. Explain your plan or provide an answer.",
  "sql": "A single, valid PostgreSQL query. Can be null."
}}

Here are the rules for choosing the mode:
1.  'summary_only': Use this for greetings, conversational responses, or questions you can answer without querying the database (e.g., "what tables do you know?"). 'sql' MUST be null.
2.  'sql_only': Use this for requests that are clearly asking for raw data without needing an explanation. 'summary' can be a brief note.
3.  'sql_and_summary': Use this for most analytical questions. The 'summary' should explain what you plan to do. The 'sql' should be the query to execute that plan.

Example 1: User asks "Hey, how are you?"
{{
  "mode": "summary_only",
  "summary": "I'm doing well, ready to help you with your data! What can I look up for you?",
  "sql": null
}}

Example 2: User asks "show me the total number of incidents"
{{
  "mode": "sql_and_summary",
  "summary": "Okay, I will run a query to count the total number of records in the 'incidents' table.",
  "sql": "SELECT COUNT(*) FROM incidents;"
}} """
        return {"role": "system", "content": system_content}

    def _manage_current_history_budget(self):
        """Trims the current_history to stay within the token budget."""
        current_tokens = sum(len(msg["content"]) / 4 for msg in self.current_history)
        while current_tokens > self.token_budget and len(self.current_history) > 2:
            removed_message = self.current_history.pop(1)
            current_tokens -= len(removed_message["content"]) / 4
            logger.info("Trimmed current history to manage token budget.")

    def get_llm_response(self, new_message: Optional[Dict] = None) -> str:
        """Central method to call the LLM and get a raw response."""
        if new_message:
            self.current_history.append(new_message)
            self.full_history.append(new_message)
        
        self._manage_current_history_budget()

        logger.info("⚡ Calling LLM...")
        start_time = time.time()
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=self.current_history,
                temperature=0.0,
                max_tokens=1500,
                response_format={"type": "json_object"},
            )
            ai_response_content = response.choices[0].message.content
            # Add AI response to both histories
            assistant_message = {"role": "assistant", "content": ai_response_content}
            self.current_history.append(assistant_message)
            self.full_history.append(assistant_message)
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"✅ AI response received ({elapsed:.2f}ms)")
            return ai_response_content
        except Exception as e:
            logger.error(f"❌ LLM API error: {e}")
            error_summary = f"Sorry, I encountered an error trying to process that request: {e}"
            error_content = json.dumps({
                "mode": "summary_only",
                "summary": error_summary,
                "sql": None
            })
            # Also log error to history
            self.current_history.append({"role": "assistant", "content": error_content})
            self.full_history.append({"role": "assistant", "content": error_content})
            return error_content

    def generate_final_summary(self, question: str, initial_summary: str, db_data: pd.DataFrame) -> str:
        # Same as before
        logger.info("✍️ Generating final, data-aware summary...")
        summary_prompt = f"""The user's original question was: '{question}'
My initial plan was: '{initial_summary}'
I executed a query and retrieved the following data (first 20 rows):
{db_data.head(20).to_string()}
Please provide a concise, natural language summary of this data that directly answers the user's question. Just provide the text, no extra formatting."""
        
        summary_history = [{"role": "user", "content": summary_prompt}]
        try:
            response = self.groq_client.chat.completions.create(model=self.model, messages=summary_history, temperature=0.1, max_tokens=1000)
            final_summary = response.choices[0].message.content
            return final_summary
        except Exception as e:
            logger.error(f"❌ LLM error during final summary generation: {e}")
            return "I was able to retrieve the data, but encountered an error while trying to summarize it."

    def execute_sql(self, sql: str) -> Union[pd.DataFrame, str]:
        # Same as before
        dangerous = ["drop", "delete", "truncate", "alter", "update", "create", "insert"]
        if any(kw in sql.lower() for kw in dangerous): return "🚫 Safety Alert: Destructive operations are blocked."
        try:
            with self.db_engine.connect() as conn:
                df = pd.read_sql(text(sql), conn)
            return df
        except Exception as e:
            return f"❌ Database error: {str(e)[:200]}"


def run_interactive_session(client_id: str):
    """Main function to run the new, structured interactive session."""
    print("\n" + "=" * 70)
    print("🚀 CONVERSATIONAL NL2SQL AGENT (v3 - Persistent History)")
    print("=" * 70)
    
    agent = None
    try:
        neo4j_config = Neo4jConfig(uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"), user=os.getenv("NEO4J_USER", "neo4j"), password=os.getenv("NEO4J_PASSWORD"), database="neo4j")
        neo4j_store = Neo4jGraphStore(neo4j_config)
        from app.core.config import Config
        Config.set_client_id(client_id)
        db_engine = Config.get_engine()
        
        agent = NL2SQLChatAgent(client_id=client_id, neo4j_store=neo4j_store, db_engine=db_engine)

        print("\n" + "-" * 70)
        print("💡 Ask questions about your data. Type 'quit' to exit.\n")
        
        # Main loop wrapped in its own try/finally to ensure history is saved
        try:
            while True:
                user_input = input("You: ").strip()
                if not user_input: continue
                if user_input.lower() in {"quit", "exit"}:
                    print("AI: Goodbye!"); break

                raw_response = agent.get_llm_response({"role": "user", "content": user_input})
                try:
                    parsed_response = json.loads(raw_response)
                    mode, summary, sql = parsed_response.get("mode"), parsed_response.get("summary"), parsed_response.get("sql")

                    if mode == "summary_only":
                        if summary: print(f"AI: {summary}")
                    elif mode == "sql_only":
                        if sql:
                            print(f"AI: Generated SQL:\n{sql}")
                            result = agent.execute_sql(sql)
                            if isinstance(result, pd.DataFrame):
                                print(f"\n📊 Results ({len(result)} rows):\n{result.head(10).to_string(index=False)}")
                            else: print(f"\n{result}")
                        else: print("AI: I was going to run a query, but didn't generate one.")
                    elif mode == "sql_and_summary":
                        if summary: print(f"AI: {summary}")
                        if sql:
                            print(f"AI: Generated SQL:\n{sql}")
                            result = agent.execute_sql(sql)
                            if isinstance(result, pd.DataFrame):
                                print(f"✅ Query executed, found {len(result)} rows. Now generating final summary...")
                                final_summary = agent.generate_final_summary(user_input, summary, result)
                                print(f"AI Summary: {final_summary}")
                            else: print(f"\n{result}")
                        else: print("AI: I was going to run a query, but didn't generate one.")
                    else: print("AI: I seem to have responded in an unknown mode.")
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode LLM JSON response: {raw_response}")
                    print("AI: I had a problem with my own response format. Please try again.")
                print("-" * 70)
        finally:
            # Save full history log when the session ends
            if agent and agent.full_history:
                log_dir = Path("artifacts/query_logs")
                log_dir.mkdir(exist_ok=True)
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                log_file = log_dir / f"conversation_log_{timestamp}.jsonl"
                with open(log_file, 'w') as f:
                    for entry in agent.full_history:
                        f.write(json.dumps(entry) + '\n')
                print(f"\n📜 Full conversation log saved to: {log_file}")

    except KeyboardInterrupt: print("\n👋 Session interrupted.")
    except Exception as e: logger.error(f"A critical error occurred: {e}", exc_info=True)
    finally:
        if 'neo4j_store' in locals() and 'agent' in locals() and agent is not None:
             neo4j_store.close()
        print("Session ended.")

if __name__ == "__main__":
    import sys
    # path setup is the same
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))
    
    from src.config import Config
    client_id_input = input("Enter client ID (e.g., c1ehs_oilgas): ").strip()
    if not client_id_input:
        print("Client ID is required for this script.")
        sys.exit(1)
        
    run_interactive_session(client_id_input)
