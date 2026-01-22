from fastapi import FastAPI, HTTPException
from neo4j import GraphDatabase
from cypher_utils import fix_order_by_alias, normalize_return, sanitize_cypher, validate_cypher
from neo4j_schema_extractor import Neo4jSchemaExtractor1
from neo4j_schema import Neo4jSchemaExtractor
from groq_cypher import GroqCypherGenerator
from neo4j_executor import Neo4jExecutor
import os

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# --- CONFIG ---
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE=os.getenv("NEO4J_DATABASE")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- INIT ---
driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

schema_extractor = Neo4jSchemaExtractor(driver)
executor = Neo4jExecutor(
    driver,
    os.getenv("NEO4J_DATABASE", "neo4j")
)
cypher_generator = GroqCypherGenerator(GROQ_API_KEY)

extractor = Neo4jSchemaExtractor1(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD,NEO4J_DATABASE)


@app.post("/ask")
def ask(question: str):
    # 1. Extract schema
    # schema = schema_extractor.extract_schema()
    schema = extractor.extract()
    print("Extracted Schema:")
    print(schema)

    
    # 2. Generate Cypher
    cypher = cypher_generator.generate_cypher(question, schema)
    print("Generating Cypher for question:")
    print(question)
    print("Generated Cypher:")
    print(cypher)   

    # 3. Safety check
    forbidden = ["CREATE", "MERGE", "DELETE", "SET", "DROP"]
    if any(x in cypher.upper() for x in forbidden):
        raise HTTPException(400, "Unsafe Cypher detected")

    # 4. Execute
    raw_cypher = cypher
    clean_cypher = sanitize_cypher(raw_cypher)
    validate_cypher(clean_cypher)
    normalized = normalize_return(clean_cypher)
    final_cypher = fix_order_by_alias(normalized)
    result = executor.run(final_cypher)
    return { "question": question, "cypher": cypher, "result": result }
    # return { "question": question, "cypher": cypher }

# uvicorn api:app --reload
# http://localhost:8000/docs
