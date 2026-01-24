class Neo4jExecutor:
    def __init__(self, driver, database):
        self.driver = driver
        self.database = database

    def run(self, cypher: str):
        with self.driver.session(database=self.database) as session:
            result = session.run(cypher)
            return [r.data() for r in result]
