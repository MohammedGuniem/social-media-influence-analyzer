from neo4j import GraphDatabase
import json


class GraphDBConnector:

    def __init__(self, host, port, user, password):
        self.driver = GraphDatabase.driver(
            F"bolt://{host}:{port}", auth=(user, password))
        self.database = "neo4j"

    def __del__(self):
        if self.driver is not None:
            self.driver.close()

    """ Writing methods """

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

    def save_node(self, node_id, node_type, node_props, network_name, submissions_type, date):
        with self.driver.session(database=self.database) as session:
            # Preparing props for ON CREATE and On MATCH for update
            node_props = self.prepare_props(pointer="n", props=node_props)
            session.write_transaction(
                self._create_or_update_node, node_id, node_type, node_props, network_name, submissions_type, date)

    def save_edge(self, from_node, to_node, edge_type, edge_props, network_name, submissions_type, date):
        with self.driver.session(database=self.database) as session:
            # Preparing props for ON CREATE and On MATCH for update
            edge_props = self.prepare_props(
                pointer="r", props=edge_props)
            session.write_transaction(
                self._create_or_update_edge, from_node, to_node, edge_type, edge_props, network_name, submissions_type, date)

    def calculate_centrality(self, network_name, date, submissions_type, centrality):
        with self.driver.session(database=self.database) as session:
            procedure_name = ""
            additional = ""
            if centrality == "degree_centrality":
                procedure_name = "gds.alpha.degree.write"
            elif centrality == "betweenness_centrality":
                procedure_name = "gds.betweenness.write"
            elif centrality == "hits_centrality_":
                procedure_name = "gds.alpha.hits.write"
                additional = ",hitsIterations: 10"
            query = (
                F"CALL {procedure_name}"
                "({ "
                F"nodeQuery: 'MATCH (n:Person) WHERE n.network = \"{network_name}\" and n.date = \"{date}\" and n.submissions_type = \"{submissions_type}\" RETURN id(n) AS id', "
                F"relationshipQuery: 'MATCH (n:Person)-[:Influences]->(m:Person) "
                F"WHERE n.network = \"{network_name}\" and n.date = \"{date}\" and n.submissions_type = \"{submissions_type}\" "
                F"and m.network = \"{network_name}\" and m.date = \"{date}\" and n.submissions_type = \"{submissions_type}\" "
                "RETURN id(n) AS source, id(m) AS target',"
                F"writeProperty: '{centrality}'"
                F"{additional}"
                "})"
            )
            result = session.write_transaction(
                self._calculate_centrality, query)
            return result

    @staticmethod
    def _create_or_update_node(tx, node_id, node_type, props, network_name, submissions_type, date):
        node_type = node_type.upper()[0] + node_type.lower()[1:]
        pointer = "n"
        # Constructing query
        query = (
            F"MERGE ({pointer}:{node_type} "
            "{"
            F"network_id: '{node_id}', "
            F"network: '{network_name}', "
            F"submissions_type: '{submissions_type}', "
            F"date: '{date}'"
            "})\n"
            F"ON CREATE SET\n"
            F"{props}"
            F"ON MATCH SET\n"
            F"{props}"
        )
        # Sending query to DB
        result = tx.run(query)

    @staticmethod
    def _create_or_update_edge(tx, from_node, to_node, edge_type, edge_props, network_name, submissions_type, date):
        edge_type = F"{edge_type[0]}{edge_type[1:]}"
        edge_pointer = "r"
        # Constructing query
        query = (
            F"MATCH (from: {from_node.type} "
            "{"
            F"network_id: '{from_node.id}', "
            F"network: '{network_name}', "
            F"date: '{date}', "
            F"submissions_type: '{submissions_type}'"
            "})\n"
            F"MATCH (to: {to_node.type} "
            "{"
            F"network_id: '{to_node.id}', "
            F"network: '{network_name}', "
            F"date: '{date}', "
            F"submissions_type: '{submissions_type}'"
            "})\n"
            F"MERGE(from)-[r:{edge_type}]->(to)\n"
            F"ON CREATE SET\n"
            F"{edge_props}\n"
            F"ON MATCH SET\n"
            F"{edge_props}"
        )
        # Sending query to DB
        result = tx.run(query)

    @staticmethod
    def _calculate_centrality(tx, query):
        result = tx.run(query)
        return result

    """ Reading methods """

    def get_centralitites_max(self, network_name, submissions_type, date):
        with self.driver.session(database=self.database) as session:
            """
            query = (
                "MATCH (n {network: '"+network_name+"', date: '"+date+"'})"
                "RETURN "
                "max(n.degree_centrality) AS max_degree, "
                "max(n.betweenness_centrality) AS max_betweenness, "
                "max(n.hits_centrality_hub) AS max_hits_hub, "
                "max(n.hits_centrality_auth) AS max_hits_auth"
            )
            """
            query = (
                "MATCH (n {"
                F"network: '{network_name}', "
                F"submissions_type: '{submissions_type}', "
                F"date: '{date}'"
                "})"
                "RETURN "
                "max(n.degree_centrality) AS max_degree, "
                "max(n.betweenness_centrality) AS max_betweenness, "
                "max(n.hits_centrality_hub) AS max_hits_hub, "
                "max(n.hits_centrality_auth) AS max_hits_auth"
            )
            centralities_max = session.read_transaction(
                self._read_centralities_max, query)
            return centralities_max

    def get_graphs(self):
        with self.driver.session() as session:
            query = (
                "MATCH(n) RETURN distinct (n.network) as network, (n.date) as date, (n.submissions_type) as submissions_type"
            )
            result = session.read_transaction(
                self._get_available_graphs, query)
            return result

    def get_graph(self, network_name, submissions_type, date, relation_type):
        with self.driver.session(database=self.database) as session:
            query = (
                "MATCH (s { "
                F"network: '{network_name}', "
                F"submissions_type: '{submissions_type}', "
                F"date: '{date}' "
                "}) "
                "MATCH (t { "
                F"network: '{network_name}', "
                F"submissions_type: '{submissions_type}', "
                F"date: '{date}' "
                "}) "
                "MATCH p=(s)-[r]->(t) "
                "WITH *, relationships(p) AS relations "
                "RETURN [relation IN relations | [startNode(relation), (relation), endNode(relation)]] as data"
            )
            graph = session.read_transaction(
                self._read_graph, query)
            centralities_max = self.get_centralitites_max(
                network_name, submissions_type, date)
            return graph, centralities_max

    def get_path(self, network_name, submissions_type, date, from_name, to_name):
        with self.driver.session(database=self.database) as session:
            query = (
                "MATCH (n { "
                F"name: '{from_name}', "
                F"network: '{network_name}', "
                F"submissions_type: '{submissions_type}', "
                F"date: '{date}' "
                "}) "
                "MATCH (m { "
                F"name: '{to_name}', "
                F"network: '{network_name}', "
                F"submissions_type: '{submissions_type}', "
                F"date: '{date}' "
                "}) "
                F"MATCH p=shortestPath((n)-[:Influences* ..]->(m)) WITH *, relationships(p) AS relations "
                F"WITH *, relationships(p) AS relations "
                F"RETURN [relation IN relations | [startNode(relation), (relation), endNode(relation)]] as data "
            )
            path_subgraph = session.read_transaction(
                self._read_graph, query)
            centralities_max = self.get_centralitites_max(
                network_name, submissions_type, date)
            return path_subgraph, centralities_max

    def filter_by_score(self, network_name, submissions_type, date, score_type, lower_score, upper_score):
        with self.driver.session(database=self.database) as session:
            lower, upper = "", ""
            if isinstance(lower_score, int):
                lower = F"{lower_score} <="
            if isinstance(upper_score, int):
                upper = F"<= {upper_score}"
            query = (
                "MATCH (n {"
                F"network: '{network_name}', "
                F"submissions_type: '{submissions_type}', "
                F"date: '{date}' "
                "}) "
                "MATCH (m {"
                F"network: '{network_name}', "
                F"submissions_type: '{submissions_type}', "
                F"date: '{date}' "
                "}) "
                "MATCH p=(n)-[r]->(m) "
                F"WHERE {lower} toInteger(r.{score_type}) {upper} "
                "WITH *, relationships(p) AS relations "
                "RETURN [relation IN relations | [startNode(relation), (relation), endNode(relation)]] as data "
            )
            result = session.read_transaction(
                self._read_graph, query)
            centralities_max = self.get_centralitites_max(
                network_name, submissions_type, date)
            return result, centralities_max

    def filter_by_influence_area(self, network_name, submissions_type, date, areas_array, operation):
        with self.driver.session(database=self.database) as session:
            if len(areas_array) > 0:
                filters = []
                for area in areas_array:
                    filters.append(F" '{area}' IN r.influence_areas ")
                filter_syntax = F' {operation} '.join(filters)
            else:
                return
            query = (
                "MATCH (n {"
                F"network: '{network_name}', "
                F"submissions_type: '{submissions_type}', "
                F"date: '{date}' "
                "}) "
                "MATCH (m {"
                F"network: '{network_name}', "
                F"submissions_type: '{submissions_type}', "
                F"date: '{date}' "
                "}) "
                "MATCH p=(n)-[r]->(m) "
                F"WHERE {filter_syntax} "
                "WITH *, relationships(p) AS relations "
                "RETURN [relation IN relations | [startNode(relation), (relation), endNode(relation)]] as data "
            )
            result = session.read_transaction(
                self._read_graph, query)
            centralities_max = self.get_centralitites_max(
                network_name, submissions_type, date)
            return result, centralities_max

    @ staticmethod
    def _get_available_graphs(tx, query):
        result = tx.run(query)
        available_graphs = []
        for record in result:
            graph = {
                "network": record["network"],
                "date": record["date"],
                "submissions_type": record["submissions_type"]
            }
            available_graphs.append(graph)
        return available_graphs

    @ staticmethod
    def _read_centralities_max(tx, query):
        result = tx.run(query)
        centralities_max = {}
        for record in result:
            centralities_max["degree_centrality"] = record["max_degree"]
            centralities_max["betweenness_centrality"] = record["max_betweenness"]
            centralities_max["hits_centrality_hub"] = record["max_hits_hub"]
            centralities_max["hits_centrality_auth"] = record["max_hits_auth"]
        return centralities_max

    @ staticmethod
    def _read_graph(tx, query):
        result = tx.run(query)
        nodes, links = [], []
        for path_array in result:
            data = path_array['data']
            for relation in data:
                start_node = dict(relation[0])
                relation_info = dict(relation[1])
                end_node = dict(relation[2])
                for this_node in [start_node, end_node]:
                    node = {}
                    node['props'] = {}
                    for attr, val in this_node.items():
                        if attr != "network_id":
                            node['props'][attr] = val
                        else:
                            node['id'] = val
                    if node not in nodes:
                        nodes.append(node)
                link = {
                    'source': start_node['network_id'],
                    'target': end_node['network_id'],
                    'props': {}
                }
                for attr, val in relation_info.items():
                    if attr != "network_id":
                        link['props'][attr] = val
                    else:
                        link['id'] = val
                if link not in links:
                    links.append(link)
        return {"nodes": nodes, "links": links}

    """ Deleting methods """

    def delete_graph(self, network_name, submissions_type, from_date, to_date):
        with self.driver.session() as session:
            query = (
                "MATCH (n {"
                F"network: '{network_name}', "
                F"submissions_type: '{submissions_type}' "
                "})"
                F"WHERE n.date >= '{from_date}' AND n.date <= '{to_date}' "
                "DETACH DELETE n"
            )

            result = session.write_transaction(
                self._delete_graph, query)
            nodes_deleted = result.consume().counters.nodes_deleted
            relationships_deleted = result.consume().counters.relationships_deleted
            return nodes_deleted, relationships_deleted

    @staticmethod
    def _delete_graph(tx, query):
        result = tx.run(query)
        for r in result:
            for r1 in r:
                print(r1)
        return result
