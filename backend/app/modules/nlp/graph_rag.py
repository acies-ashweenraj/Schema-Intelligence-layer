from neo4j import GraphDatabase

from app.modules.nlp.neo4j_schema_extractor import Neo4jSchemaExtractor1
from app.modules.nlp.neo4j_executor import Neo4jExecutor
from app.modules.nlp.groq_cypher import GroqCypherGenerator
from app.modules.nlp.groq_client import GroqClient

from app.modules.nlp.cypher_utils import (
    sanitize_cypher,
    validate_cypher,
    normalize_return,
    fix_order_by_alias,
)


class GraphRAG:
    def __init__(
        self,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        neo4j_database: str,
        groq_api_key: str,
    ):
        self.driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password),
        )

        self.database = neo4j_database

        self.schema_extractor = Neo4jSchemaExtractor1(
            uri=neo4j_uri,
            user=neo4j_user,
            password=neo4j_password,
            database=neo4j_database,
        )

        self.executor = Neo4jExecutor(self.driver, neo4j_database)
        self.cypher_generator = GroqCypherGenerator(groq_api_key)
        self.groq = GroqClient(groq_api_key)

    def close(self):
        try:
            self.driver.close()
        except Exception:
            pass

    def ask(self, question: str) -> str:
        # 1) Extract schema
        schema = self.schema_extractor.extract()

        # 2) Generate cypher using Groq
        cypher = self.cypher_generator.generate_cypher(question, str(schema))

        # 3) Clean + validate cypher
        clean = sanitize_cypher(cypher)
        validate_cypher(clean)
        normalized = normalize_return(clean)
        final_cypher = fix_order_by_alias(normalized)

        # ✅ log cypher in terminal only
        print("\n==============================")
        print("QUESTION:", question)
        print("CYPHER:\n", final_cypher)
        print("==============================\n")

        # 4) Execute
        rows = self.executor.run(final_cypher)

        # 5) Return summary answer only
        return self._summarize(question, rows)

    def _summarize(self, question: str, rows: list) -> str:
        if not rows:
            return "No results found in the knowledge graph."

        prompt = f"""
You are a helpful assistant.

User question:
{question}

Neo4j query results:
{rows}

Answer in short summary (1-3 lines).
Do not mention cypher or database.
"""

        return self.groq.chat(prompt).strip()
