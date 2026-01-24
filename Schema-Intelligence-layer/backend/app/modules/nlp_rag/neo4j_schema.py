from neo4j import GraphDatabase

class Neo4jSchemaExtractor:

    def __init__(self, driver):
        self.driver = driver

    def extract_schema(self) -> str:
        query = """
        CALL db.schema.visualization()
        YIELD nodes, relationships
        RETURN nodes, relationships
        """

        with self.driver.session() as session:
            result = session.run(query).single()

        nodes = result["nodes"]
        rels = result["relationships"]

        node_labels = set()
        rel_types = set()

        for n in nodes:
            labels = n.get("labels")
            if labels:
                node_labels.update(labels)

        for r in rels:
            rtype = r.get("type")
            if isinstance(rtype, str):
                rel_types.add(rtype)

        return f"""
Nodes:
{", ".join(sorted(node_labels))}

Relationships:
{", ".join(sorted(rel_types))}
"""