from classes.modelling.TextClassification import TextClassifier
from classes.modelling.Node import Node
from classes.modelling.Edge import Edge


class Graph:
    def __init__(self, mongo_db_connector, neo4j_db_connector):
        self.mongo_db_connector = mongo_db_connector
        self.neo4j_db_connector = neo4j_db_connector
        self.text_classifier = TextClassifier(mongo_db_connector)
        self.nodes = {}
        self.edges = {}

    def addOrUpdateEdge(self, from_node_id, relation_type, to_node_id, influence_area, group_name, interaction_score, activity_score, upvotes_score):
        edge_id = F"{from_node_id}_{relation_type}_{to_node_id}"
        if edge_id not in self.edges:
            edge = Edge(from_node_id, relation_type,
                        to_node_id, [], [], interaction_score, activity_score, upvotes_score)
        else:
            edge = self.edges[edge_id]

        edge.influence_areas.append(influence_area)
        edge.group_names.append(group_name)
        edge.updateScore(interaction_score, activity_score, upvotes_score)

        self.edges[edge_id] = edge

    def save(self, network_name, date):
        # Saving nodes in neo4j database graph.
        for node in self.nodes.values():
            self.neo4j_db_connector.save_node(
                node_id=node.id,
                node_type=node.type,
                node_props=node.props,
                network_name=network_name,
                date=date
            )

        # Saving edges in neo4j database graph.
        for edge in self.edges.values():
            if edge.from_node in self.nodes and edge.to_node in self.nodes:
                self.neo4j_db_connector.save_edge(
                    from_node=self.nodes[edge.from_node],
                    to_node=self.nodes[edge.to_node],
                    edge_type=edge.relation_type,
                    edge_props=edge.getProps(),
                    network_name=network_name,
                    date=date
                )
