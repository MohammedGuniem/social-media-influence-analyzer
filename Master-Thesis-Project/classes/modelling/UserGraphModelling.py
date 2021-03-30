from classes.modelling.GraphModelling import Graph
from classes.modelling.Node import Node
from classes.modelling.Edge import Edge


class UserGraph(Graph):
    def __init__(self, mongo_db_connector, neo4j_db_connector):
        super().__init__(mongo_db_connector, neo4j_db_connector)

    def addOrUpdateNode(self, activity_object, node_type):
        if node_id not in self.nodes:
            node_id = activity_object["author_id"]
            node = Node(
                id=node_id,
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
        edge.update_score(interaction_score, activity_score, upvotes_score)

        self.edges[edge_id] = edge

    def build_model(self, network_name, group_name, submissions_type):

        # Get group information.
        group = self.mongo_db_connector.getGroupInfo(
            network_name, display_name=group_name)

        # Get all submissions on this group.
        group_id = group['id']
        submissions = self.mongo_db_connector.getSubmissionsOnGroup(
            network_name, submissions_type, group_id)

        for submission in submissions:
            influence_area = self.text_classifier.classify_title(
                submission['title'])

            # add submission authors as nodes
            self.addOrUpdateNode(
                activity_object=submission, node_type="Redditor")

            # Get all comments on submissions on this group
            comments = self.mongo_db_connector.getCommentsOnSubmission(
                network_name,
                submission_type,
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
                        submission_type=submission_type,
                        comment_id=parent_id
                    )
                    if not parent_comment:
                        continue
                    from_node_id = parent_comment["author_id"]
                    upvotes_weight = parent_comment["upvotes"]

                interaction_weight = 1
                activity_weight = 1 + \
                    self.mongo_db_connector.get_children_count(
                        network_name, submissions_type, [comment])

                # add comment authors as nodes
                self.add_node(activity_object=comment, node_type="Redditor")

                # Draw influence relation between authors/commenters and child commenters
                self.add_edge(
                    from_node_id=from_node_id,
                    relation_type="Influences",
                    to_node_id=comment_author_id,
                    influence_area=influence_area,
                    group_name=group_name,
                    interaction_score=interaction_weight,
                    activity_score=activity_weight,
                    upvotes_score=upvotes_weight
                )
