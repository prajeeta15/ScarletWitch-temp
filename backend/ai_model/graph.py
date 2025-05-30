from neo4j import GraphDatabase

class DarkWebGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def add_marketplace_data(self, name, category, threat_level):
        with self.driver.session() as session:
            session.write_transaction(self._create_node, name, category, threat_level)

    @staticmethod
    def _create_node(tx, name, category, threat_level):
        tx.run(
            "MERGE (m:Marketplace {name: $name}) "
            "SET m.category = $category, m.threat_level = $threat_level",
            name=name, category=category, threat_level=threat_level
        )

    def relate_users_and_marketplaces(self, user_id, marketplace):
        with self.driver.session() as session:
            session.write_transaction(self._create_relationship, user_id, marketplace)

    @staticmethod
    def _create_relationship(tx, user_id, marketplace):
        tx.run(
            "MERGE (u:User {id: $user_id}) "
            "MERGE (m:Marketplace {name: $marketplace}) "
            "MERGE (u)-[:VISITED]->(m)",
            user_id=user_id, marketplace=marketplace
        )

# Usage
graph = DarkWebGraph("bolt://localhost:7687", "neo4j", "password")
graph.add_marketplace_data("AlphaBay", "Drugs", "High")
graph.relate_users_and_marketplaces("user123", "AlphaBay")
graph.close()
