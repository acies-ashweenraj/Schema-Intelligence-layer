import os
import json
from typing import Any, Dict, List

from neo4j import GraphDatabase
from dotenv import load_dotenv

from .groq_cypher import GroqCypherGenerator
from .neo4j_executor import Neo4jExecutor
from .neo4j_schema_extractor import Neo4jSchemaExtractor1
from .cypher_utils import sanitize_cypher, validate_cypher, normalize_return, fix_order_by_alias,fix_aggregate_where
from .groq_client import GroqClient

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def _safe_json(obj: Any):
    """Convert Neo4j types to JSON-safe values."""
    try:
        return json.loads(json.dumps(obj, default=str))
    except Exception:
        return str(obj)


def summarize_answer(question: str, data: List[Dict[str, Any]]) -> str:
    """
    Uses Groq to convert raw Neo4j result into a clean chatbot summary.
    """
    client = GroqClient(GROQ_API_KEY)

    # keep only first 20 rows for summary
    sample = data[:20]

    prompt = f"""
You are a chatbot assistant.
User asked: {question}

Here is the database output (JSON list):
{json.dumps(sample, indent=2, default=str)}

Rules:
- Give ONLY a short human summary (2-4 lines)
- Do NOT show JSON
- Do NOT show cypher
- If list is empty -> say: "No matching records found."
- If results contain names/titles, list them nicely.
- If results contain counts, explain top results clearly.
"""

    return client.chat(prompt).strip()


def ask_question(req) -> Dict[str, Any]:
    """
    req must contain:
      - neo4j_uri
      - neo4j_user
      - neo4j_password
      - neo4j_database
      - question
    """

    # 1) Connect to Neo4j
    driver = GraphDatabase.driver(
        req.neo4j_uri,
        auth=(req.neo4j_user, req.neo4j_password)
    )

    executor = Neo4jExecutor(
        uri=req.neo4j_uri,
        user=req.neo4j_user,
        password=req.neo4j_password,
        database=req.neo4j_database
    )

    extractor = Neo4jSchemaExtractor1(
        uri=req.neo4j_uri,
        user=req.neo4j_user,
        password=req.neo4j_password,
        database=req.neo4j_database
    )

    cypher_generator = GroqCypherGenerator(GROQ_API_KEY)

    try:
        # 2) Extract schema
        schema = extractor.extract()

        # 3) Generate cypher
        cypher = cypher_generator.generate_cypher(req.question, schema)

        # 4) Clean & validate cypher
        raw_cypher = cypher
        clean_cypher = sanitize_cypher(raw_cypher)
        clean_cypher = fix_aggregate_where(clean_cypher)
        validate_cypher(clean_cypher)

        normalized = normalize_return(clean_cypher)
        final_cypher = fix_order_by_alias(normalized)

        # 5) Execute query
        result_data = executor.run(final_cypher)

        # 6) Summarize
        summary = summarize_answer(req.question, result_data)

        return {
            "answer": summary,      # ✅ only chatbot summary
                # optional: keep for frontend table
        }

    finally:
        driver.close()
        extractor.close()
