from groq import Groq


class GroqCypherGenerator:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def generate_cypher(self, question: str, schema: str) -> str:
        prompt = f"""
You are an expert Neo4j Cypher developer.

Graph schema:
{schema}

Rules:
- Generate READ-ONLY Cypher
CRITICAL RULES (must be followed exactly):
- Generate READ-ONLY Cypher only
- Use ONLY the provided schema
- Do NOT hallucinate labels, relationships, or properties
- Do NOT use CREATE, MERGE, DELETE, SET
- Relationship direction must be ignored
- NEVER use size((n)--()) or size((n)-[]-())
- To count relationships, ALWAYS use: COUNT {{ (n)--() }}
- NEVER use ORDER BY count(x)
- ALWAYS use WITH ... count(x) AS alias
- ORDER BY must reference the alias
- If schema is empty, return: // Schema not available
- Return Cypher ONLY (no explanation, no markdown)

Question:
{question}
"""

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return response.choices[0].message.content.strip()
