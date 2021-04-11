from neo4j import GraphDatabase
import json


class GraphDBConnector:

    def __init__(self, host, port, user, password):
        self.driver = GraphDatabase.driver(
            F"bolt://{host}:{port}", auth=(user, password))
        self.database = "neo4j"

    def __del__(self):
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

    def save_node(self, node_id, node_type, node_props, network_name, date):
        with self.driver.session(database=self.database) as session:

            # Preparing props for ON CREATE and On MATCH for update
            node_props = self.prepare_props(pointer="n", props=node_props)

            session.write_transaction(
                self._create_or_update_node, node_id, node_type, node_props, network_name, date)

    def save_edge(self, from_node, to_node, edge_type, edge_props, network_name, date):
        with self.driver.session(database=self.database) as session:

            # Preparing props for ON CREATE and On MATCH for update
            edge_props = self.prepare_props(
                pointer="r", props=edge_props)

            session.write_transaction(
                self._create_or_update_edge, from_node, to_node, edge_type, edge_props, network_name, date)

    def calculate_centrality(self, network_name, date, centrality):
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
                F"nodeQuery: 'MATCH (n:Person) WHERE n.network = \"{network_name}\" and n.date = \"{date}\" RETURN id(n) AS id', "
                F"relationshipQuery: 'MATCH (n:Person)-[:Influences]->(m:Person) "
                F"WHERE n.network = \"{network_name}\" and n.date = \"{date}\" "
                F"and m.network = \"{network_name}\" and m.date = \"{date}\" "
                "RETURN id(n) AS source, id(m) AS target',"
                F"writeProperty: '{centrality}'"
                F"{additional}"
                "})"
            )
            result = session.write_transaction(
                self._calculate_centrality, query)
            return result

    @staticmethod
    def _create_or_update_node(tx, node_id, node_type, props, network_name, date):
        node_type = node_type.upper()[0] + node_type.lower()[1:]
        pointer = "n"

        # Constructing query
        query = "MERGE ("+pointer+":"+node_type + \
            " {network_id: '"+node_id+"', network: '" + \
                network_name+"', date: '"+date+"'})"
        query += "\nON CREATE SET\n"
        query += props
        query += "\nON MATCH SET\n"
        query += props

        # Sending query to DB
        result = tx.run(query)

    @staticmethod
    def _create_or_update_edge(tx, from_node, to_node, edge_type, edge_props, network_name, date):
        edge_type = F"{edge_type[0]}{edge_type[1:]}"
        edge_pointer = "r"

        # Constructing query
        query = ""
        query += "MATCH (from:"+from_node.type + \
            " { network_id: '"+from_node.id+"', network: '" + \
            network_name+"', date: '"+date+"' })\n"
        query += "MATCH (to:"+to_node.type + \
            " { network_id: '"+to_node.id+"', network: '" + \
            network_name+"', date: '"+date+"'  })\n"
        query += "MERGE(from)-[r:"+edge_type+"]->(to)"
        query += "\nON CREATE SET\n"
        query += edge_props
        query += "\nON MATCH SET\n"
        query += edge_props

        # Sending query to DB
        result = tx.run(query)

    @staticmethod
    def _calculate_centrality(tx, query):
        result = tx.run(query)
        return result

    """ Reading methods """

    def get_user_graphs(self):
        with self.driver.session() as session:
            query = (
                "MATCH(n) RETURN distinct (n.network) as network, (n.date) as date"
            )
            result = session.read_transaction(
                self._get_available_user_graphs, query)
            return result

    def get_graph(self, network_name, date, relation_type):
        with self.driver.session(database=self.database) as session:
            query = (
                "MATCH(n { "
                F"network: '{network_name}', "
                F"date: '{date}' "
                "}) "
                "MATCH (s { "
                F"network: '{network_name}', "
                F"date: '{date}' "
                "})-[r]->(t { "
                F"network: '{network_name}', "
                F"date: '{date}' "
                "}) "
            )
            nodes = session.read_transaction(
                self._get_graph_nodes, query)

            links = session.read_transaction(
                self._get_graph_links, query)

            graph = {
                "nodes": nodes,
                "links": links
            }

            query = (
                "MATCH (n {network: '"+network_name+"', date: '"+date+"'})"
                "RETURN "
                "max(n.degree_centrality) AS max_degree, "
                "max(n.betweenness_centrality) AS max_betweenness, "
                "max(n.hits_centrality_hub) AS max_hits_hub, "
                "max(n.hits_centrality_auth) AS max_hits_auth"
            )
            centralities_max = session.read_transaction(
                self._read_centralities_max, query)

            return graph, centralities_max

    def get_path(self, network_name, date, from_name, to_name, database):
        with self.driver.session(database=self.database) as session:
            query = (
                "MATCH (n {name: '"+from_name + "', network: '" +
                network_name+"', date: '"+date+"'}) "
                "MATCH (m {name: '"+to_name + "', network: '" +
                network_name+"', date: '"+date+"'}) "
                "MATCH p=(n)-[:Influences* ..]->(m) "
                "WITH *, relationships(p) AS relations "
                "RETURN [relation IN relations | [startNode(relation), (relation), endNode(relation)]] as data "
            )

            result = session.read_transaction(
                self._read_graph, query)
            return result

    def filter_by_score(self, network_name, date, score_type, lower_score, upper_score, database):
        with self.driver.session(database=self.database) as session:
            lower, upper = "", ""
            if isinstance(lower_score, int):
                lower = F"{lower_score} <="
            if isinstance(upper_score, int):
                upper = F"<= {upper_score}"
            query = (
                "MATCH (n {network: '"+network_name+"', date: '"+date+"'}) "
                "MATCH (m {network: '"+network_name+"', date: '"+date+"'})) "
                "MATCH p=(n)-[r]->(m) "
                F"WHERE {lower} toInteger(r.{score_type}) {upper} "
                "WITH *, relationships(p) AS relations "
                "RETURN [relation IN relations | [startNode(relation), (relation), endNode(relation)]] as data "
            )
            result = session.read_transaction(
                self._read_graph, query)
            return result

    def filter_by_influence_area(self, network_name, date, areas_array, operation, database):
        with self.driver.session(database=self.database) as session:
            if len(areas_array) > 0:
                filters = []
                for area in areas_array:
                    filters.append(F" '{area}' IN r.influence_areas ")
                filter_syntax = F' {operation} '.join(filters)
            else:
                return

            query = (
                "MATCH (n {network: '"+network_name+"', date: '"+date+"'}) "
                "MATCH (m {network: '"+network_name+"', date: '"+date+"'}) "
                "MATCH p=(n)-[r]->(m) "
                F"WHERE {filter_syntax} "
                "WITH *, relationships(p) AS relations "
                "RETURN [relation IN relations | [startNode(relation), (relation), endNode(relation)]] as data "
            )
            result = session.read_transaction(
                self._read_graph, query)
            return result

    @staticmethod
    def _get_graph_nodes(tx, query):
        query = query + "RETURN distinct n AS node"
        result = tx.run(query)
        nodes = []
        for record in result:
            node = {}
            node['id'] = record["node"]['network_id']
            node['props'] = {}
            for prop, val in record["node"].items():
                if prop != "network_id":
                    node['props'][prop] = val
            if node not in nodes:
                nodes.append(node)
        return nodes

    @staticmethod
    def _get_graph_links(tx, query):
        query = query + "RETURN distinct s AS source, r AS relation, t AS target"
        result = tx.run(query)
        links = []
        for record in result:
            relation = {}
            relation['source'] = record["source"]['network_id']
            relation['target'] = record["target"]['network_id']
            relation['props'] = {}
            for prop, val in record["relation"].items():
                relation['props'][prop] = val
            if relation not in links:
                links.append(relation)
        return links

    @ staticmethod
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
                    node['props'] = {}
                    for attr, val in this_node.items():
                        if attr != "network_id":
                            node['props'][attr] = val
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

    @ staticmethod
    def _read_centralities_max(tx, query):
        result = tx.run(query)
        centralities_max = {}
        for record in result:
            centralities_max["degree"] = record["max_degree"]
            centralities_max["betweenness"] = record["max_betweenness"]
            centralities_max["hits_hub"] = record["max_hits_hub"]
            centralities_max["hits_auth"] = record["max_hits_auth"]
        return centralities_max

    @ staticmethod
    def _get_available_user_graphs(tx, query):
        result = tx.run(query)
        available_graphs = []
        for record in result:
            graph = {
                "network": record["network"],
                "date": record["date"]
            }
            available_graphs.append(graph)

        return available_graphs
