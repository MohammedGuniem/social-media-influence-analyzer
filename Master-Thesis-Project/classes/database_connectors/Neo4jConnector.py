from neo4j import GraphDatabase
import json


class GraphDBConnector:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def set_database(self, database_name):
        self.database = database_name
        self.create_or_replace_database(database_name)

    def save_node(self, node_id, node_type, node_props):
        with self.driver.session(database=self.database) as session:

            # Preparing props for ON CREATE and On MATCH for update
            node_props = self.prepare_props(pointer="n", props=node_props)

            session.write_transaction(
                self._create_or_update_node, node_id, node_type, node_props)

    def save_edge(self, from_node, to_node, edge_type, edge_props):
        with self.driver.session(database=self.database) as session:

            # Preparing props for ON CREATE and On MATCH for update

            edge_props = self.prepare_props(
                pointer="r", props=edge_props)

            session.write_transaction(
                self._create_or_update_edge, from_node, to_node, edge_type, edge_props)

    def create_or_replace_database(self, database_name):
        with self.driver.session() as session:
            session.write_transaction(
                self._create_or_replace_database, database_name)

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
    def _create_or_update_node(tx, node_id, node_type, props):
        node_type = node_type.upper()[0] + node_type.lower()[1:]
        pointer = "n"

        # Constructing query
        query = "MERGE ("+pointer+":"+node_type + \
            " {network_id: '"+node_id+"'})"
        query += "\nON CREATE SET\n"
        query += props
        query += "\nON MATCH SET\n"
        query += props

        # Sending query to DB
        result = tx.run(query)

    @staticmethod
    def _create_or_update_edge(tx, from_node, to_node, edge_type, edge_props):
        edge_type = F"{edge_type.upper()[0]}{edge_type.lower()[1:]}"
        edge_pointer = "r"

        # Constructing query
        query = ""
        query += "MATCH (from:"+from_node['type'] + \
            " { network_id: '"+from_node['id']+"' })\n"
        query += "MATCH (to:"+to_node['type'] + \
            " { network_id: '"+to_node['id']+"' })\n"
        query += "MERGE(from)-[r:"+edge_type+"]->(to)"
        query += "\nON CREATE SET\n"
        query += edge_props
        query += "\nON MATCH SET\n"
        query += edge_props

        # Sending query to DB
        result = tx.run(query)

    @staticmethod
    def _create_or_replace_database(tx, database_name):

        # Constructing query
        query = F"CREATE OR REPLACE DATABASE {database_name}"

        # Sending query to DB
        result = tx.run(query)
