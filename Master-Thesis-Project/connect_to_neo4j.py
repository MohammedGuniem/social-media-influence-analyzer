from neo4j import GraphDatabase


class WriteToNeo4jDatabase:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def prepare_props(self, node_type, props):
        props_str = ""
        for key, value in props.items():
            props_str += F"{node_type.lower()[0]}.{key} = '{value}', "
        return props_str[:-2].replace("'[", "[").replace("]'", "]")

    def create_pair(self, from_node_type, from_node_id, from_node_props, relationship_type, relationship_id, relationship_props, to_node_type, to_node_id, to_node_props):

        from_node_props = self.prepare_props("FROM", from_node_props)
        relationship_props = self.prepare_props(
            "RELATIONSHIP", relationship_props)
        to_node_props = self.prepare_props("TO", to_node_props)

        with self.driver.session() as session:
            session.write_transaction(
                self._create_or_update_pair, from_node_type, from_node_id, from_node_props, relationship_type, relationship_id, relationship_props, to_node_type, to_node_id, to_node_props)

    @staticmethod
    def _create_or_update_pair(tx, from_node_type, from_node_id, from_node_props, relationship_type, relationship_id, relationship_props, to_node_type, to_node_id, to_node_props):
        result = tx.run("MERGE (f:" + from_node_type + " {name: $from_node_id})"
                        "MERGE (t:" + to_node_type + " {name: $to_node_id})"
                        "MERGE(f)-[r:" + relationship_type + "]->(t)"
                        "ON CREATE SET "
                        F"{from_node_props}, "
                        F"{relationship_props}, "
                        F"{to_node_props} "
                        "ON MATCH SET "
                        F"{from_node_props}, "
                        F"{relationship_props}, "
                        F"{to_node_props} "
                        "RETURN f, r, t", to_node_type=to_node_type, from_node_id=from_node_id, to_node_id=to_node_id)
        return result.single()


if __name__ == "__main__":
    from_node_type = "Person"
    from_user_id = "P1"
    from_user_data = {"fullname": "User A", "age": 40, "work": "engineer"}

    relationship_type = "DOES_INFLUENCE"
    relationship_id = "R1"
    relationship_data = {"weight": 2, "area": ["Politics"]}

    to_node_type = "Person"
    to_user_id = "P2"
    to_user_data = {"fullname": "User B", "age": 60, "work": "doctor"}

    neo4j_writer = WriteToNeo4jDatabase(
        "bolt://localhost:7687", "neo4j", "1234")
    neo4j_writer.create_pair(from_node_type, from_user_id, from_user_data,
                             relationship_type, relationship_id, relationship_data,
                             to_node_type, to_user_id, to_user_data)
    neo4j_writer.close()
