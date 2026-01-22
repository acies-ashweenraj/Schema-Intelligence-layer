from app.modules.Kg.semantic_router import get_node_label, get_property_name


class NodeLoader:
    def __init__(self, neo4j):
        self.neo4j = neo4j

    def delete_all_nodes(self):
        self.neo4j.run("MATCH (n) DETACH DELETE n")

    def load_node(self, table, row, pk, table_desc, column_desc_map):
        label = get_node_label(table, table_desc)

        props = {
            get_property_name(c, column_desc_map.get(c, "")): v
            for c, v in row.items()
        }

        pk_prop = get_property_name(pk, column_desc_map.get(pk, ""))

        # ✅ ALWAYS USE BACKTICKS
        self.neo4j.run(
            f"""
            MERGE (n:{label} {{ `{pk_prop}`: $pk }})
            SET n += $props
            """,
            {"pk": row[pk], "props": props},
        )
