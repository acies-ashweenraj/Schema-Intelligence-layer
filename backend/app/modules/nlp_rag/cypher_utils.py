import re

FORBIDDEN_KEYWORDS = ["CREATE", "MERGE", "DELETE", "SET", "DROP"]

def sanitize_cypher(cypher: str) -> str:
    # Remove markdown fences
    cypher = re.sub(r"```(?:cypher)?", "", cypher, flags=re.IGNORECASE)
    cypher = cypher.replace("```", "")
    return cypher.strip()


def validate_cypher(cypher: str):
    upper = cypher.upper()

    # Block writes
    for kw in FORBIDDEN_KEYWORDS:
        if kw in upper:
            raise ValueError(f"Forbidden Cypher keyword detected: {kw}")

    # Must start with MATCH / WITH / CALL
    if not upper.startswith(("MATCH", "WITH", "CALL", "OPTIONAL MATCH")):
        raise ValueError("Cypher must start with MATCH / WITH / CALL")

    # Only ONE RETURN
    if upper.count(" RETURN ") > 1:
        raise ValueError("Multiple RETURN clauses detected")


def normalize_return(cypher: str) -> str:
    """
    Ensures RETURN is only at the end
    """
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
    """
    Ensures ORDER BY uses a valid alias from RETURN
    """
    lines = [l.strip() for l in cypher.splitlines() if l.strip()]

    return_line = next(l for l in lines if l.upper().startswith("RETURN"))
    order_by_lines = [l for l in lines if l.upper().startswith("ORDER BY")]

    # No ORDER BY → nothing to fix
    if not order_by_lines:
        return cypher

    # Extract aliases from RETURN
    aliases = re.findall(r"AS\s+(\w+)", return_line, re.IGNORECASE)

    if not aliases:
        return cypher  # Can't fix without alias

    alias = aliases[0]

    fixed_lines = []
    for line in lines:
        if line.upper().startswith("ORDER BY"):
            fixed_lines.append(f"ORDER BY {alias} DESC")
        else:
            fixed_lines.append(line)

    return "\n".join(fixed_lines)