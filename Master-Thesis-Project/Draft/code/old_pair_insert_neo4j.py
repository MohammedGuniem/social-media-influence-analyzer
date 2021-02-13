
# Delete this method when done improving
@staticmethod
def _create_or_update_pair(tx, from_node_type, from_node_id, from_node_props, relationship_type, relationship_id, relationship_props, to_node_type, to_node_id, to_node_props):
    result = tx.run("MERGE (f:" + from_node_type + " { id: $from_node_id })"
                    "MERGE (t:" + to_node_type + " { id: $to_node_id })"
                    "MERGE(f)-[r:" + relationship_type + "]->(t)"
                    "ON CREATE SET "
                    F"{from_node_props}"
                    F"{relationship_props}"
                    F"{to_node_props}"
                    "ON MATCH SET "
                    F"{from_node_props}"
                    F"{relationship_props}"
                    F"{to_node_props}"
                    "RETURN f, r, t", from_node_id=from_node_id, to_node_id=to_node_id)
    return result.single()
