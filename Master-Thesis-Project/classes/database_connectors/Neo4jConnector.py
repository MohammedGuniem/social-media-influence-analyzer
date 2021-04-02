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
        edge_type = F"{edge_type[0]}{edge_type[1:]}"
        edge_pointer = "r"

        # Constructing query
        query = ""
        query += "MATCH (from:"+from_node.type + \
            " { network_id: '"+from_node.id+"' })\n"
        query += "MATCH (to:"+to_node.type + \
            " { network_id: '"+to_node.id+"' })\n"
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

    def get_user_graphs(self):
        with self.driver.session() as session:
            query = (
                "SHOW DATABASES WHERE name STARTS WITH 'usergraph'"
            )
            result = session.read_transaction(
                self._get_available_user_graphs, query)
            return result

    def get_graph(self, database):
        with self.driver.session(database=database) as session:
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

    def get_path(self, from_name, to_name, database):
        with self.driver.session(database=database) as session:
            query = (
                "MATCH (n {name: '"+from_name + "'}) "
                "MATCH (m {name: '"+to_name + "'}) "
                "MATCH p=(n)-[:Influences* ..]->(m) "
                "WITH *, relationships(p) AS relations "
                "RETURN [relation IN relations | [startNode(relation), (relation), endNode(relation)]] as data "
            )

            result = session.read_transaction(
                self._read_graph, query)
            return result

    def filter_by_score(self, score_type, lower_score, upper_score, database):
        with self.driver.session(database=database) as session:
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

    def filter_by_influence_area(self, areas_array, operation, database):
        with self.driver.session(database=database) as session:
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

    def get_degree_centrality(self, database, score_type):
        with self.driver.session(database=database) as session:
            query = ("MATCH()-[r] -> () "
                     "CALL gds.alpha.degree.stream({ "
                     "nodeProjection: 'Redditor', "
                     "relationshipProjection: { "
                     "  Influences: { "
                     "    type: 'Influences', "
                     F"    properties: '{score_type}' "
                     "  } "
                     "}, "
                     F"  relationshipWeightProperty: '{score_type}' "
                     "}) "
                     "YIELD nodeId, score "
                     "RETURN gds.util.asNode(nodeId).name AS name, score/sum(r.total) as centrality "
                     "ORDER BY centrality DESC "
                     )
            result = session.read_transaction(
                self._calculate_centrality, query)
            return result

    def get_betweenness_centrality(self, database):
        with self.driver.session(database=database) as session:
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

    def get_hits_centrality(self, database):
        with self.driver.session(database=database) as session:
            hitsIterations = 5
            user_centrality = {}
            while True:
                query = ("CALL gds.alpha.hits.stream({ "
                         F"hitsIterations: {hitsIterations}, "
                         "nodeProjection: 'Redditor',  "
                         "relationshipProjection: 'Influences' "
                         "}) "
                         "YIELD nodeId, values "
                         "RETURN gds.util.asNode(nodeId).name AS name, {auth: values.auth, hub: values.hub} AS centrality "
                         )
                centrality = session.read_transaction(
                    self._calculate_centrality, query)

                if centrality.keys() == user_centrality.keys():
                    break
                else:
                    user_centrality = centrality
                    hitsIterations += 5
            return centrality, hitsIterations

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
                        'groups': relation_node['groups'],
                        'interaction': relation_node['interaction'],
                        'activity': relation_node['activity'],
                        'upvotes': relation_node['upvotes'],
                        'interaction_and_activity':  relation_node['interaction_and_activity'],
                        'interaction_and_upvotes': relation_node['interaction_and_upvotes'],
                        'activity_and_upvotes': relation_node['activity_and_upvotes'],
                        'total': relation_node['total']
                    }
                }
                if relation not in links:
                    links.append(relation)

        return {"nodes": nodes, "links": links}

    @staticmethod
    def _calculate_centrality(tx, query):
        result = tx.run(query)
        centrality = {}
        for record in result:
            centrality[record['name']] = record['centrality']
        return centrality

    @staticmethod
    def _get_available_user_graphs(tx, query):
        result = tx.run(query)
        available_databases = []
        for record in result:
            db = record["name"].replace("usergraph", "")
            db = db[0:4] + "-" + db[4:6] + "-" + db[6:8]
            available_databases.append(db)

        return available_databases
