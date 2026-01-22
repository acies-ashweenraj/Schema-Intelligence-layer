import os
import psycopg2
from neo4j import GraphDatabase, basic_auth

from app.modules.Kg.semantic_router import (
    get_node_label,
    get_property_name,
    get_relationship_name,
    set_llm_usage
)


# ✅ internal defaults (user will NOT send these)
RESET_GRAPH_DEFAULT = True
ROW_LIMIT_DEFAULT = None   # None = load all rows
USE_LLM_DEFAULT = True


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
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema=%s AND table_name=%s
            ORDER BY ordinal_position
        """, (schema, t))
        cols = [{"name": r[0], "datatype": r[1], "description": r[0]} for r in cur.fetchall()]

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
        edges = [{"column_name": r[0], "parent_table": r[1], "parent_column": r[2]} for r in cur.fetchall()]

        schema_data.append({
            "table": t,
            "short_description": t,
            "columns": cols,
            "edges": edges
        })

    return schema_data


def ensure_neo4j_database(driver, db_name: str):
    """
    Try to create DB if Enterprise.
    If Community -> fallback to neo4j.
    """
    try:
        with driver.session(database="system") as session:
            session.run(f"CREATE DATABASE {db_name} IF NOT EXISTS")
        return db_name
    except Exception:
        return "neo4j"


def load_kg(payload):
    # internal defaults
    reset_graph = RESET_GRAPH_DEFAULT
    row_limit = ROW_LIMIT_DEFAULT
    use_llm = USE_LLM_DEFAULT

    # set LLM usage in semantic router
    set_llm_usage(use_llm)

    if use_llm and not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY missing in .env (required for LLM naming)")

    # connect postgres
    pg = psycopg2.connect(
        host=payload.pg.host,
        port=payload.pg.port,
        database=payload.pg.database,
        user=payload.pg.username,
        password=payload.pg.password,
    )
    cur = pg.cursor()
    schema = payload.pg.schema_name

    # connect neo4j
    driver = GraphDatabase.driver(
        payload.neo4j.uri,
        auth=basic_auth(payload.neo4j.user, payload.neo4j.password),
        encrypted=False
    )

    # create db name automatically
    kg_db_name = f"kg_{payload.pg.database}"
    kg_db = ensure_neo4j_database(driver, kg_db_name)

    # extract schema
    schema_data = extract_schema_from_postgres(cur, schema)

    # reset graph
    if reset_graph:
        with driver.session(database=kg_db) as session:
            session.run("MATCH (n) DETACH DELETE n")

    loaded_rows = 0
    created_relationships = 0

    for table in schema_data:
        table_name = table["table"]
        table_desc = table["short_description"]
        label = get_node_label(table_name, table_desc)

        sql = f'SELECT * FROM "{schema}"."{table_name}"'
        if row_limit:
            sql += f" LIMIT {int(row_limit)}"

        cur.execute(sql)
        colnames = [d[0].lower() for d in cur.description]
        pk_col = colnames[0]

        column_desc_map = {c["name"].lower(): c["description"] for c in table["columns"]}

        rows = cur.fetchall()

        for r in rows:
            row_dict = dict(zip(colnames, r))

            props = {
                get_property_name(c, column_desc_map.get(c, "")): row_dict[c]
                for c in colnames
            }

            pk_prop = get_property_name(pk_col, column_desc_map.get(pk_col, ""))

            with driver.session(database=kg_db) as session:
                session.run(
                    f"""
                    MERGE (n:{label} {{ {pk_prop}: $pk }})
                    SET n += $props
                    """,
                    {"pk": row_dict[pk_col], "props": props},
                )

            loaded_rows += 1

            # relationships
            for edge in table["edges"]:
                fk_col = edge["column_name"].lower()
                fk_val = row_dict.get(fk_col)
                if fk_val is None:
                    continue

                parent_table = edge["parent_table"]
                parent_schema = next(t for t in schema_data if t["table"] == parent_table)

                parent_label = get_node_label(parent_table, parent_schema["short_description"])
                rel_type = get_relationship_name(
                    table_name,
                    parent_table,
                    table_desc,
                    parent_schema["short_description"],
                )

                fk_prop = get_property_name(fk_col, column_desc_map.get(fk_col, ""))
                parent_pk_col = edge["parent_column"].lower()
                parent_pk_prop = get_property_name(parent_pk_col, parent_pk_col)

                with driver.session(database=kg_db) as session:
                    session.run(
                        f"""
                        MATCH (c:{label} {{ {fk_prop}: $v }})
                        MATCH (p:{parent_label} {{ {parent_pk_prop}: $v }})
                        MERGE (c)-[:{rel_type}]->(p)
                        """,
                        {"v": fk_val},
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
