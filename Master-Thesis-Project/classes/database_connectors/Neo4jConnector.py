from neo4j import GraphDatabase


class GraphDBConnector:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def addNode(self, ID, Type, props):
        with self.driver.session() as session:

            # Preparing props for ON CREATE and On MATCH for update
            props = self.prepare_props(pointer="n", props=props)

            session.write_transaction(
                self._create_or_update_node, ID, Type, props)

    def addEdge(self, relation_Type, relation_props, from_ID, from_Type, to_ID, to_Type):
        with self.driver.session() as session:

            # Preparing props for ON CREATE and On MATCH for update

            relation_props = self.prepare_props(
                pointer="r", props=relation_props)

            session.write_transaction(
                self._create_or_update_edge, relation_Type, relation_props, from_ID, from_Type, to_ID, to_Type)

    def __del__(self):
        self.driver.close()

    def prepare_props(self, pointer, props):
        props_query = ""
        for key, prop in props.items():
            props_query += pointer+"."+key.lower()
            if isinstance(prop, list):
                props_query += " = "+str(prop)+",\n"
            elif isinstance(prop, dict):
                props_query += " = '"+json.dumps(prop)+"',\n"
            else:
                props_query += " = '"+str(prop)+"',\n"
        props_query = props_query[:-2]
        return props_query

    @staticmethod
    def _create_or_update_node(tx, ID, Type, props):
        Type = Type.upper()[0] + Type.lower()[1:]
        pointer = "n"

        # Constructing query
        query = "MERGE ("+pointer+":"+Type+" {network_ID: '"+ID+"'})"
        query += "\nON CREATE SET\n"
        query += props
        query += "\nON MATCH SET\n"
        query += props

        # Sending query to DB
        result = tx.run(query)

    @staticmethod
    def _create_or_update_edge(tx, relation_Type, relation_props, from_ID, from_Type, to_ID, to_Type):
        relation_Type = relation_Type.upper()[0] + relation_Type.lower()[1:]
        relation_pointer = "r"
        relation_ID = from_ID+"_"+to_ID

        # Constructing query
        query = ""
        query += "MATCH (from:"+from_Type+" { network_ID: '"+from_ID+"' })\n"
        query += "MATCH (to:"+to_Type+" { network_ID: '"+to_ID+"' })\n"
        query += "MERGE(from)-[r:"+relation_Type+"]->(to)"
        query += "\nON CREATE SET\n"
        query += relation_props
        query += "\nON MATCH SET\n"
        query += relation_props

        # Sending query to DB
        result = tx.run(query)
