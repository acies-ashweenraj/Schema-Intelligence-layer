from neo4j import GraphDatabase


class Neo4jExecutor:
    def __init__(self, uri: str, user: str, password: str, database: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def run(self, cypher: str):
        with self.driver.session(database=self.database) as session:
            result = session.run(cypher)
            return [r.data() for r in result]
