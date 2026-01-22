import os
from groq import Groq

MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def _get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY missing in .env")
    return Groq(api_key=api_key)


def call_llm(prompt: str) -> str:
    client = _get_client()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=50,
    )
    return resp.choices[0].message.content.strip()


def llm_table_label(description: str) -> str:
    return call_llm(f"""
You are generating a Neo4j NODE LABEL.

DESCRIPTION:
{description}

RULES:
- Output EXACTLY ONE label
- Represents a REAL-WORLD business entity
- Singular noun
- PascalCase
- No abbreviations
- No technical words
- Max 3 words

FORBIDDEN:
table, record, data, mapping, xref, history, master, detail

OUTPUT:
LabelOnly
""")


def llm_column_name(description: str) -> str:
    return call_llm(f"""
You are generating a Neo4j NODE PROPERTY NAME.

DESCRIPTION:
{description}

RULES:
- Output EXACTLY ONE property name
- camelCase
- Business meaning only
- No abbreviations
- No technical words
- No IDs unless unavoidable
- Max 3 words

OUTPUT:
propertyNameOnly
""")


def llm_relationship_name(child_desc: str, parent_desc: str) -> str:
    return call_llm(f"""
You are generating a Neo4j RELATIONSHIP TYPE.

CHILD ENTITY DESCRIPTION:
{child_desc}

PARENT ENTITY DESCRIPTION:
{parent_desc}

RULES:
- Output EXACTLY ONE relationship name
- ALL CAPS
- Verb-based
- Business meaning
- Direction: CHILD → PARENT

OUTPUT:
RELATIONSHIP_ONLY
""")
