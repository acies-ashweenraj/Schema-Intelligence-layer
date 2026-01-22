from groq import Groq
import json


class GroqSummarizer:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def summarize(self, question: str, rows: list) -> str:
        # keep payload small
        sample = rows[:20]

        prompt = f"""
You are a chatbot answering user questions from Neo4j query results.

User Question:
{question}

Neo4j Result Rows (JSON):
{json.dumps(sample, indent=2)}

Rules:
- Give a short human readable summary
- If empty result -> say no matching records found
- If list -> highlight top findings
- Do not mention cypher query
- Do not mention Neo4j
- Keep answer within 2-5 lines
"""

        resp = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return resp.choices[0].message.content.strip()
