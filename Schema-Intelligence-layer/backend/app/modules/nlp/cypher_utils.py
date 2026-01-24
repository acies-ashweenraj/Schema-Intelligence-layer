import re

FORBIDDEN_KEYWORDS = ["CREATE", "MERGE", "DELETE", "SET", "DROP"]

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

def normalize_return(cypher: str) -> str:
    lines = [l.strip() for l in cypher.splitlines() if l.strip()]

    match_lines = []
    return_line = None

    for line in lines:
        if line.upper().startswith("RETURN"):
            return_line = line
        else:
            match_lines.append(line)

    if not return_line:
        raise ValueError("No RETURN clause found")

    return "\n".join(match_lines + [return_line])

def fix_order_by_alias(cypher: str) -> str:
    lines = [l.strip() for l in cypher.splitlines() if l.strip()]

    if not any(l.upper().startswith("ORDER BY") for l in lines):
        return cypher

    return_line = next((l for l in lines if l.upper().startswith("RETURN")), None)
    if not return_line:
        return cypher

    aliases = re.findall(r"AS\s+(\w+)", return_line, re.IGNORECASE)
    if not aliases:
        return cypher

    alias = aliases[0]

    fixed = []
    for line in lines:
        if line.upper().startswith("ORDER BY"):
            fixed.append(f"ORDER BY {alias} DESC")
        else:
            fixed.append(line)

    return "\n".join(fixed)

def fix_with_aliases(cypher: str) -> str:
    """
    WITH s.stafffullname, incidentCount  -> WITH s.stafffullname AS stafffullname, incidentCount
    """
    lines = cypher.splitlines()
    fixed = []

    for line in lines:
        if line.strip().upper().startswith("WITH "):
            body = line.strip()[5:].strip()
            parts = [p.strip() for p in body.split(",")]

            new_parts = []
            for p in parts:
                if re.search(r"\s+AS\s+", p, flags=re.IGNORECASE):
                    new_parts.append(p)
                    continue

                if "." in p and "(" not in p and ")" not in p:
                    alias = p.split(".")[-1]
                    new_parts.append(f"{p} AS {alias}")
                else:
                    new_parts.append(p)

            fixed.append("WITH " + ", ".join(new_parts))
        else:
            fixed.append(line)

    return "\n".join(fixed)

import re

def fix_aggregate_where(cypher: str) -> str:
    """
    Fixes patterns like:
    WHERE MAX(x.prop) = something
    Neo4j doesn't allow aggregate in WHERE.
    """
    pattern = r"WHERE\s+MAX\((.*?)\)\s*=\s*(\w+)"
    if re.search(pattern, cypher, re.IGNORECASE):
        # remove invalid WHERE MAX(...)
        cypher = re.sub(pattern, "", cypher, flags=re.IGNORECASE)
    return cypher.strip()

