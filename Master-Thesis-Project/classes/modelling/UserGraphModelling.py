from classes.modelling.TextClassification import TextClassifier
from classes.modelling.Node import Node
from classes.modelling.Edge import Edge


class UserGraph:
    def __init__(self, mongo_db_connector, neo4j_db_connector):
        self.text_classifier = TextClassifier(mongo_db_connector)
        self.mongo_db_connector = mongo_db_connector
        self.neo4j_db_connector = neo4j_db_connector
        self.nodes = {}
        self.edges = {}

    def addOrUpdateNode(self, activity_object, node_type):
        node_id = activity_object["author_id"]
        if node_id not in self.nodes:
            node = Node(
                ID=node_id,
                Type=node_type,
                Props={
                    'network_id': node_id,
                    'name': activity_object['author_name'],
                    'author_id': activity_object["author_id"]
                }
            )
            self.nodes[node_id] = node

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

    def build(self, network_name, submissions_type):

        groups = self.mongo_db_connector.getGroups(network_name)

        for group in groups:
            group_name = group['display_name']

            # Get group information.
            group_info = self.mongo_db_connector.getGroupInfo(
                network_name, display_name=group_name)

            # Get all submissions on this group.
            group_id = group_info['id']
            submissions = self.mongo_db_connector.getSubmissionsOnGroup(
                network_name, submissions_type, group_id)

            for submission in submissions:
                influence_area = self.text_classifier.classify_title(
                    submission['body'])

                # add submission authors as nodes
                self.addOrUpdateNode(
                    activity_object=submission, node_type="Redditor")

                # Get all comments on submissions on this group
                comments = self.mongo_db_connector.getCommentsOnSubmission(
                    network_name,
                    submissions_type,
                    "t3_"+submission['id']
                )

                for comment in comments:
                    comment_author_id = comment['author_id']

                    parent_id_prefix = comment['parent_id'][0:2]
                    parent_id = comment['parent_id'][3:]

                    # Comment is top-level
                    if parent_id_prefix == "t3":
                        from_node_id = submission["author_id"]
                        upvotes_weight = submission["upvotes"]

                    # Comment is a thread comment
                    elif parent_id_prefix == "t1":
                        parent_comment = self.mongo_db_connector.getCommentInfo(
                            network_name=network_name,
                            submissions_type=submissions_type,
                            comment_id=parent_id
                        )
                        if not parent_comment:
                            continue
                        from_node_id = parent_comment["author_id"]
                        upvotes_weight = parent_comment["upvotes"]

                    interaction_weight = 1
                    activity_weight = 1 + \
                        self.mongo_db_connector.getChildrenCount(
                            network_name, submissions_type, [comment])

                    # add comment authors as nodes
                    self.addOrUpdateNode(
                        activity_object=comment, node_type="Redditor")

                    # Draw influence relation between authors/commenters and child commenters
                    self.addOrUpdateEdge(
                        from_node_id=from_node_id,
                        relation_type="Influences",
                        to_node_id=comment_author_id,
                        influence_area=influence_area,
                        group_name=group_name,
                        interaction_score=interaction_weight,
                        activity_score=activity_weight,
                        upvotes_score=upvotes_weight
                    )

    def save(self, database_name):
        # Create or clear/replace database
        self.neo4j_db_connector.set_database(database_name)

        # Saving nodes in neo4j database graph.
        for node in self.nodes.values():
            self.neo4j_db_connector.save_node(
                node.id, node.type, node.props
            )

        # Saving edges in neo4j database graph.
        for edge in self.edges.values():
            if edge.from_node in self.nodes and edge.to_node in self.nodes:
                self.neo4j_db_connector.save_edge(
                    from_node=self.nodes[edge.from_node],
                    to_node=self.nodes[edge.to_node],
                    edge_type=edge.relation_type,
                    edge_props=edge.getProps()
                )
