import re

FORBIDDEN_KEYWORDS = ["CREATE", "MERGE", "DELETE", "SET", "DROP", "REMOVE", "CALL apoc"]


def sanitize_cypher(cypher: str) -> str:
    cypher = re.sub(r"```(?:cypher)?", "", cypher, flags=re.IGNORECASE)
    cypher = cypher.replace("```", "")
    return cypher.strip()


def validate_cypher(cypher: str):
    upper = cypher.upper()

    for kw in FORBIDDEN_KEYWORDS:
        if kw in upper:
            raise ValueError(f"Forbidden Cypher keyword detected: {kw}")

    if not upper.startswith(("MATCH", "WITH", "CALL", "OPTIONAL MATCH")):
        raise ValueError("Cypher must start with MATCH / WITH / CALL")

    if "RETURN" not in upper:
        raise ValueError("Cypher must contain RETURN")

    if upper.count(" RETURN ") > 1:
        raise ValueError("Multiple RETURN clauses detected")
