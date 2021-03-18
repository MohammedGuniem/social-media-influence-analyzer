from neo4j import GraphDatabase
import json


class GraphDBConnector:

    def __init__(self, uri, user, password, database_name=""):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database_name

    """ Writing methods """

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
                props_query += ' = '+str(prop).replace("'", '"')+',\n'
            elif isinstance(prop, dict):
                props_query += ' = "'+json.dumps(prop).replace('"', "'")+'",\n'
            elif isinstance(prop, int):
                props_query += ' = '+str(prop).replace('"', "'")+',\n'
            else:
                props_query += ' = "'+str(prop).replace('"', "'")+'",\n'
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

    """ Reading methods """

    def get_graph(self):
        with self.driver.session(database=self.database) as session:
            query = (
                "MATCH (n) "
                "MATCH (m) "
                "MATCH p=(n)-[:Influences*..]->(m) "
                "WITH *, relationships(p) AS relations "
                "RETURN [relation IN relations | [startNode(relation), (relation), endNode(relation)]] as data "
            )
            result = session.read_transaction(
                self._read_graph, query)
            return result

    def get_path(self, from_name, to_name, shortestPath):
        with self.driver.session(database=self.database) as session:
            if shortestPath:
                path = "MATCH p=shortestPath((n)-[:Influences* ..]->(m)) "
            else:
                path = "MATCH p=(n)-[:Influences* ..]->(m) "
            query = (
                "MATCH (n {name: '"+from_name + "'}) "
                "MATCH (m {name: '"+to_name + "'}) "
                F"{path}"
                "WITH *, relationships(p) AS relations "
                "RETURN [relation IN relations | [startNode(relation), (relation), endNode(relation)]] as data "
            )

            result = session.read_transaction(
                self._read_graph, query)
            return result

    def filter_by_score(self, score_type, lower_score, upper_score):
        with self.driver.session(database=self.database) as session:
            lower, upper = "", ""
            if isinstance(lower_score, int):
                lower = F"{lower_score} <="
            if isinstance(upper_score, int):
                upper = F"<= {upper_score}"
            query = (
                "MATCH (n) "
                "MATCH (m) "
                "MATCH p=(n)-[r]->(m) "
                F"WHERE {lower} toInteger(r.{score_type}) {upper} "
                "WITH *, relationships(p) AS relations "
                "RETURN [relation IN relations | [startNode(relation), (relation), endNode(relation)]] as data "
            )
            result = session.read_transaction(
                self._read_graph, query)
            return result

    def filter_by_influence_area(self, areas_array, operation):
        with self.driver.session(database=self.database) as session:
            if len(areas_array) > 0:
                filters = []
                for area in areas_array:
                    filters.append(F" '{area}' IN r.influence_areas ")
                filter_syntax = F' {operation} '.join(filters)
            else:
                return

            query = ("MATCH(n) "
                     "MATCH (m) "
                     "MATCH p=(n)-[r]->(m) "
                     F"WHERE {filter_syntax} "
                     "WITH *, relationships(p) AS relations "
                     "RETURN [relation IN relations | [startNode(relation), (relation), endNode(relation)]] as data "
                     )
            result = session.read_transaction(
                self._read_graph, query)
            return result

    def get_degree_centrality(self):
        with self.driver.session(database=self.database) as session:
            query = ("MATCH()-[r] -> () "
                     "CALL gds.alpha.degree.stream({ "
                     "nodeProjection: 'Redditor', "
                     "relationshipProjection: { "
                     "  Influences: { "
                     "    type: 'Influences', "
                     "    properties: 'all_influence_score' "
                     "  } "
                     "}, "
                     "  relationshipWeightProperty: 'all_influence_score' "
                     "}) "
                     "YIELD nodeId, score "
                     "RETURN gds.util.asNode(nodeId).name AS name, score/sum(r.all_influence_score) as centrality "
                     "ORDER BY centrality DESC "
                     )
            result = session.read_transaction(
                self._calculate_centrality, query)
            return result

    def get_betweenness_centrality(self):
        with self.driver.session(database=self.database) as session:
            query = ("MATCH p=shortestPath((n)-[:Influences* ..]->(m)) "
                     "WHERE n.name <> m.name "
                     "CALL gds.betweenness.stream({ "
                     "  nodeProjection: 'Redditor', "
                     "  relationshipProjection: 'Influences' "
                     "}) "
                     "YIELD nodeId, score "
                     "RETURN gds.util.asNode(nodeId).name AS name, round(score/count(p), 3) as centrality "
                     "ORDER BY centrality DESC "
                     )
            result = session.read_transaction(
                self._calculate_centrality, query)
            return result

    @staticmethod
    def _read_graph(tx, query):
        result = tx.run(query)
        nodes, links = [], []

        for path_array in result:
            data = path_array['data']
            for relation in data:
                start_node = dict(relation[0])
                relation_node = dict(relation[1])
                end_node = dict(relation[2])
                for this_node in [start_node, end_node]:
                    node = {}
                    node['id'] = this_node['network_id']
                    node['props'] = {'name': this_node['name'],
                                     'author_id': this_node['author_id']}
                    if node not in nodes:
                        nodes.append(node)

                relation = {
                    'source': start_node['network_id'],
                    'target': end_node['network_id'],
                    'props': {
                        'influence_areas': relation_node['influence_areas'],
                        'subreddits': relation_node['subreddits'],
                        'connection_influence_score': relation_node['connection_influence_score'],
                        'activity_influence_score': relation_node['activity_influence_score'],
                        'upvotes_influence_score': relation_node['upvotes_influence_score'],
                        'connection_and_activity_influence_score':  relation_node['connection_and_activity_influence_score'],
                        'connection_and_upvotes_influence_score': relation_node['connection_and_upvotes_influence_score'],
                        'activity_and_upvotes_influence_score': relation_node['activity_and_upvotes_influence_score'],
                        'all_influence_score': relation_node['all_influence_score']
                    }
                }
                if relation not in links:
                    links.append(relation)

        return {"nodes": nodes, "links": links}

    @staticmethod
    def _calculate_centrality(tx, query):
        result = tx.run(query)
        ordered_users = []
        ordered_user_centrality = []
        for record in result:
            ordered_users.append(record['name'])
            ordered_user_centrality.append(record['centrality'])
        return ordered_users, ordered_user_centrality
