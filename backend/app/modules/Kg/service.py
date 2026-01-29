import os
from decimal import Decimal

import psycopg2
from neo4j import GraphDatabase, basic_auth

from app.modules.Kg.semantic_router import (
    get_node_label,
    get_property_name,
    get_relationship_name,
    set_llm_usage
)

# -----------------------------
# Defaults
# -----------------------------
RESET_GRAPH_DEFAULT = True
ROW_LIMIT_DEFAULT = None
USE_LLM_DEFAULT = True


# -----------------------------
# Neo4j-safe conversion
# -----------------------------
def neo4j_safe(value):
    if isinstance(value, Decimal):
        return float(value)  # use str(value) if precision matters
    return value


# -----------------------------
# Extract schema + FKs
# -----------------------------
def extract_schema_from_postgres(cur, schema: str):
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema=%s AND table_type='BASE TABLE'
        ORDER BY table_name
    """, (schema,))
    tables = [r[0] for r in cur.fetchall()]

    schema_data = []

    for t in tables:
        # columns
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema=%s AND table_name=%s
            ORDER BY ordinal_position
        """, (schema, t))
        cols = [
            {"name": r[0], "datatype": r[1], "description": r[0]}
            for r in cur.fetchall()
        ]

        # foreign keys
        cur.execute("""
            SELECT
                kcu.column_name,
                ccu.table_name AS parent_table,
                ccu.column_name AS parent_column
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
              ON ccu.constraint_name = tc.constraint_name
             AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type='FOREIGN KEY'
              AND tc.table_schema=%s
              AND tc.table_name=%s
        """, (schema, t))
        edges = [
            {
                "column_name": r[0],
                "parent_table": r[1],
                "parent_column": r[2],
            }
            for r in cur.fetchall()
        ]

        schema_data.append({
            "table": t,
            "short_description": t,
            "columns": cols,
            "edges": edges,
        })

    return schema_data


# -----------------------------
# Primary key detection (CRITICAL)
# -----------------------------
def get_primary_key(cur, schema: str, table: str):
    cur.execute("""
        SELECT a.attname
        FROM pg_index i
        JOIN pg_attribute a
          ON a.attrelid = i.indrelid
         AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = %s::regclass
          AND i.indisprimary
    """, (f"{schema}.{table}",))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"No primary key found for {schema}.{table}")
    return row[0].lower()


# -----------------------------
# Neo4j DB handling
# -----------------------------
def ensure_neo4j_database(driver, db_name: str):
    try:
        with driver.session(database="system") as session:
            session.run(f"CREATE DATABASE {db_name} IF NOT EXISTS")
        return db_name
    except Exception:
        return "neo4j"


# -----------------------------
# MAIN LOADER
# -----------------------------
def load_kg(payload):
    reset_graph = RESET_GRAPH_DEFAULT
    row_limit = ROW_LIMIT_DEFAULT
    use_llm = USE_LLM_DEFAULT

    set_llm_usage(use_llm)

    if use_llm and not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY missing in .env")

    # PostgreSQL
    pg = psycopg2.connect(
        host=payload.pg.host,
        port=payload.pg.port,
        database=payload.pg.database,
        user=payload.pg.username,
        password=payload.pg.password,
    )
    cur = pg.cursor()
    schema = payload.pg.schema_name

    # Neo4j
    driver = GraphDatabase.driver(
        payload.neo4j.uri,
        auth=basic_auth(payload.neo4j.user, payload.neo4j.password),
        encrypted=False
    )

    kg_db = ensure_neo4j_database(
        driver, f"kg_{payload.pg.database}"
    )

    schema_data = extract_schema_from_postgres(cur, schema)

    # Reset graph
    if reset_graph:
        with driver.session(database=kg_db) as session:
            session.run("MATCH (n) DETACH DELETE n")

    loaded_rows = 0
    created_relationships = 0

    # -----------------------------
    # Load nodes
    # -----------------------------
    for table in schema_data:
        table_name = table["table"]
        table_desc = table["short_description"]
        label = get_node_label(table_name, table_desc)

        pk_col = get_primary_key(cur, schema, table_name)

        sql = f'SELECT * FROM "{schema}"."{table_name}"'
        if row_limit:
            sql += f" LIMIT {int(row_limit)}"

        cur.execute(sql)
        colnames = [d[0].lower() for d in cur.description]
        rows = cur.fetchall()

        column_desc_map = {
            c["name"].lower(): c["description"]
            for c in table["columns"]
        }

        pk_prop = get_property_name(
            pk_col, column_desc_map.get(pk_col, "")
        )

        for r in rows:
            row_dict = dict(zip(colnames, r))

            props = {
                get_property_name(c, column_desc_map.get(c, "")):
                neo4j_safe(row_dict[c])
                for c in colnames
            }

            with driver.session(database=kg_db) as session:
                session.run(
                    f"""
                    MERGE (n:{label} {{ {pk_prop}: $pk }})
                    SET n += $props
                    """,
                    {
                        "pk": neo4j_safe(row_dict[pk_col]),
                        "props": props,
                    }
                )

            loaded_rows += 1

    # -----------------------------
    # Load relationships (CORRECT)
    # -----------------------------
    for table in schema_data:
        table_name = table["table"]
        table_desc = table["short_description"]
        label = get_node_label(table_name, table_desc)

        pk_col = get_primary_key(cur, schema, table_name)
        pk_prop = get_property_name(pk_col, pk_col)

        sql = f'SELECT * FROM "{schema}"."{table_name}"'
        cur.execute(sql)

        colnames = [d[0].lower() for d in cur.description]
        rows = cur.fetchall()

        for r in rows:
            row_dict = dict(zip(colnames, r))
            child_pk_val = neo4j_safe(row_dict[pk_col])

            for edge in table["edges"]:
                fk_col = edge["column_name"].lower()
                fk_val = row_dict.get(fk_col)

                if fk_val is None:
                    continue

                parent_table = edge["parent_table"]
                parent_schema = next(
                    t for t in schema_data if t["table"] == parent_table
                )

                parent_label = get_node_label(
                    parent_table,
                    parent_schema["short_description"]
                )

                parent_pk_prop = get_property_name(
                    edge["parent_column"].lower(),
                    edge["parent_column"]
                )

                rel_type = get_relationship_name(
                    table_name,
                    parent_table,
                    table_desc,
                    parent_schema["short_description"],
                )

                with driver.session(database=kg_db) as session:
                    session.run(
                        f"""
                        MATCH (c:{label} {{ {pk_prop}: $child_pk }})
                        MATCH (p:{parent_label} {{ {parent_pk_prop}: $parent_pk }})
                        MERGE (c)-[:{rel_type}]->(p)
                        """,
                        {
                            "child_pk": child_pk_val,
                            "parent_pk": neo4j_safe(fk_val),
                        }
                    )

                created_relationships += 1

    driver.close()
    cur.close()
    pg.close()

    return {
        "status": "success",
        "neo4j_database": kg_db,
        "tables_loaded": len(schema_data),
        "rows_loaded": loaded_rows,
        "relationships_created": created_relationships,
    }
