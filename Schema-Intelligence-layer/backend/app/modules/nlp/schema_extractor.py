from neo4j import GraphDatabase


class Neo4jSchemaExtractor:
    def __init__(self, uri: str, user: str, password: str, database: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    def extract_schema_text(self) -> str:
        """
        Extract schema without APOC.
        Uses only db.labels(), db.relationshipTypes(), db.propertyKeys().
        """
        with self.driver.session(database=self.database) as session:
            labels = [r["label"] for r in session.run("CALL db.labels()")]
            rels = [r["relationshipType"] for r in session.run("CALL db.relationshipTypes()")]
            props = [r["propertyKey"] for r in session.run("CALL db.propertyKeys()")]

        return f"""
Node Labels:
{", ".join(sorted(labels))}

Relationship Types:
{", ".join(sorted(rels))}

Property Keys:
{", ".join(sorted(props))}
"""
