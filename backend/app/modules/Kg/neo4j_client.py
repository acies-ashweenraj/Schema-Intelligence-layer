from neo4j import GraphDatabase, basic_auth


class Neo4jClient:
    def __init__(self, uri, user, password, database="neo4j"):
        self.database = database
        self.driver = GraphDatabase.driver(
            uri,
            auth=basic_auth(user, password),
            encrypted=False,
        )

    def close(self):
        self.driver.close()

    def run(self, query, params=None):
        with self.driver.session(database=self.database) as session:
            session.run(query, params or {})
