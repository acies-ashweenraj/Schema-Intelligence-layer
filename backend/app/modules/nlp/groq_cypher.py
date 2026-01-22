from groq import Groq

class GroqCypherGenerator:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def generate_cypher(self, question: str, schema: str) -> str:
        prompt = f"""
You are an expert Neo4j Cypher developer.

Graph schema:
{schema}

Your job:
Generate a VALID Cypher query that can run in Neo4j.

CRITICAL RULES (must follow exactly):
1) Generate READ-ONLY Cypher only.
2) Use ONLY schema labels, relationship types, and properties from schema.
3) NEVER use: CREATE, MERGE, DELETE, SET, DROP
4) Always return something using RETURN.
5) If user asks for "top N" → use ORDER BY + LIMIT N.
6) NEVER use COUNT((n)--()) or COUNT((n)-[]-())  ❌ invalid
   Instead ALWAYS use: COUNT {{ (n)--() }}  ✅ valid
7) Aggregations rules:
   - If you use COUNT(), SUM(), AVG(), MAX(), MIN() you MUST group using WITH.
   - You CANNOT use MAX(x) inside WHERE directly.
     Correct example:
       WITH s, MAX(e.riskLevel) AS maxRisk
       WHERE maxRisk = 5
8) If you use WITH and select properties, ALWAYS alias them:
   Example:
      WITH s.stafffullname AS staffName, COUNT(e) AS incidentCount
      RETURN staffName, incidentCount
9) RETURN must be at the end.
10) No markdown, no explanation, output ONLY the Cypher query.

Question:
{question}
"""

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return response.choices[0].message.content.strip()
