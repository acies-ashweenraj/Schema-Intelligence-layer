from neo4j import GraphDatabase

class Neo4jSchemaExtractor1:
    def __init__(self, uri: str, user: str, password: str, database: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    @staticmethod
    def _get_labels(tx):
        return [r["label"] for r in tx.run("CALL db.labels()")]

    @staticmethod
    def _infer_node_properties(tx, label):
        query = f"""
        MATCH (n:`{label}`)
        WITH n LIMIT 50
        UNWIND keys(n) AS key
        RETURN DISTINCT key
        """
        return [r["key"] for r in tx.run(query)]

    @staticmethod
    def _infer_relationships(tx, label):
        query = f"""
        MATCH (a:`{label}`)-[r]-(b)
        RETURN DISTINCT type(r) AS type, labels(b)[0] AS target
        """
        return [{"type": r["type"], "target": r["target"]} for r in tx.run(query)]

    def extract(self) -> dict:
        schema = {}

        with self.driver.session(database=self.database) as session:
            labels = session.execute_read(self._get_labels)

            for label in labels:
                schema[label] = {
                    "properties": session.execute_read(self._infer_node_properties, label),
                    "relationships": session.execute_read(self._infer_relationships, label),
                }

        return {"schema": schema}
