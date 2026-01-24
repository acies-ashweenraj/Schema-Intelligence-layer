from neo4j import GraphDatabase
import json


class Neo4jSchemaExtractor1:
    def __init__(self, uri: str, user: str, password: str, database: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    # ---------- Internal helpers ----------

    @staticmethod
    def _get_labels(tx):
        return [r["label"] for r in tx.run("CALL db.labels()")]

    @staticmethod
    def _get_constraints(tx):
        query = """
        SHOW CONSTRAINTS
        YIELD name, type, labelsOrTypes, properties
        RETURN collect({
            name: name,
            type: type,
            labelsOrTypes: labelsOrTypes,
            properties: properties
        }) AS constraints
        """
        record = tx.run(query).single()
        return record["constraints"] if record else []

    @staticmethod
    def _get_indexes(tx):
        query = """
        SHOW INDEXES
        YIELD name, type, labelsOrTypes, properties
        RETURN collect({
            name: name,
            type: type,
            labelsOrTypes: labelsOrTypes,
            properties: properties
        }) AS indexes
        """
        record = tx.run(query).single()
        return record["indexes"] if record else []

    @staticmethod
    def _infer_node_properties(tx, label):
        query = f"""
        MATCH (n:`{label}`)
        WITH n LIMIT 50
        UNWIND keys(n) AS key
        RETURN DISTINCT key
        """
        return {r["key"]: "string" for r in tx.run(query)}

    @staticmethod
    def _infer_relationships(tx, label):
        query = f"""
        MATCH (a:`{label}`)-[r]->(b)
        RETURN DISTINCT type(r) AS type, labels(b)[0] AS target
        """
        return [
            {
                "type": r["type"],
                "direction": "OUT",
                "target": r["target"]
            }
            for r in tx.run(query)
        ]

    # ---------- Public API ----------

    def extract(self) -> dict:
        schema = {}

        with self.driver.session(database=self.database) as session:
            labels = session.execute_read(self._get_labels)

            for label in labels:
                schema[label] = {
                    "properties": session.execute_read(
                        self._infer_node_properties, label
                    ),
                    "relationships": session.execute_read(
                        self._infer_relationships, label
                    )
                }

            constraints = session.execute_read(self._get_constraints)
            indexes = session.execute_read(self._get_indexes)

        return {
            "schema": schema,
            "constraints": constraints,
            "indexes": indexes
        }

    def extract_to_file(self, file_path: str):
        data = self.extract()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return file_path
