import os
import sys
from dotenv import load_dotenv
from kg_schema_loader import (GraphClient, GraphSchemaGenerator, GraphOrchestrator)

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# --- Argument Parsing ---
if len(sys.argv) > 1:
    SEMANTIC_CATALOG_PATH = sys.argv[1]
else:
    print("Usage: python run_loader.py <path_to_schema_file.json>")
    sys.exit(1)

# --- File Check ---
if not os.path.exists(SEMANTIC_CATALOG_PATH):
    print(f"Error: Input file '{SEMANTIC_CATALOG_PATH}' not found.")
    sys.exit(1)

# --- Neo4j Connection & Loading ---
client = None
try:
    client = GraphClient(
        uri=NEO4J_URI,
        user=NEO4J_USER,
        password=NEO4J_PASSWORD,
        database=NEO4J_DATABASE
    )

    generator = GraphSchemaGenerator(client)
    orchestrator = GraphOrchestrator(generator)

    print(f"Loading schema from '{SEMANTIC_CATALOG_PATH}' into Neo4j...")
    orchestrator.run(SEMANTIC_CATALOG_PATH)
    print("Knowledge Graph loaded successfully!")

except Exception as e:
    print(f"Error loading Knowledge Graph: {e}")

finally:
    if client:
        client.close()
