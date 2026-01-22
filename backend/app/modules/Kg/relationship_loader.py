from app.modules.Kg.semantic_router import (
    get_node_label,
    get_property_name,
    get_relationship_name,
)


class RelationshipLoader:
    def __init__(self, neo4j):
        self.neo4j = neo4j

    def create_relationship(
        self,
        child_table,
        parent_table,
        fk_column,
        parent_pk,
        row,
        child_desc,
        parent_desc,
        column_desc_map,
    ):
        fk_val = row.get(fk_column)
        if fk_val is None:
            return

        rel = get_relationship_name(child_table, parent_table, child_desc, parent_desc)

        c_label = get_node_label(child_table, child_desc)
        p_label = get_node_label(parent_table, parent_desc)

        fk_prop = get_property_name(fk_column, column_desc_map.get(fk_column, ""))
        pk_prop = get_property_name(parent_pk, column_desc_map.get(parent_pk, ""))

        # ✅ ALWAYS USE BACKTICKS
        self.neo4j.run(
            f"""
            MATCH (c:{c_label} {{ `{fk_prop}`: $v }})
            MATCH (p:{p_label} {{ `{pk_prop}`: $v }})
            MERGE (c)-[:{rel}]->(p)
            """,
            {"v": fk_val},
        )
