from classes.modelling.GraphModelling import Graph
from classes.modelling.Node import Node
from classes.modelling.Edge import Edge


class UserGraph(Graph):
    def __init__(self, mongo_db_connector, neo4j_db_connector, network_name, submissions_type, date):
        self.network_name = network_name
        self.submissions_type = submissions_type
        super().__init__(mongo_db_connector, neo4j_db_connector,
                         network_name, submissions_type, date)

    def addOrUpdateNode(self, activity_object, node_type):
        node_id = activity_object["author_id"]
        if node_id not in self.nodes:
            node = Node(
                ID=node_id,
                Type=node_type,
                Props={
                    'type': node_type,
                    'network_id': node_id,
                    'name': activity_object['author_name'],
                    'author_id': activity_object["author_id"]
                }
            )
            self.nodes[node_id] = node

    def build(self):

        groups = self.mongo_db_connector.getGroups(
            self.network_name, self.submissions_type)

        for group in groups:
            group_name = group['display_name']

            # Get group information.
            group_info = self.mongo_db_connector.getGroupInfo(
                self.network_name, self.submissions_type, display_name=group_name)

            # Get all submissions on this group.
            group_id = group_info['id']
            submissions = self.mongo_db_connector.getSubmissionsOnGroup(
                self.network_name, self.submissions_type, group_id)

            for submission in submissions:
                influence_area = self.text_classifier.classify_title(
                    submission['body'])

                # add submission authors as nodes
                self.addOrUpdateNode(
                    activity_object=submission, node_type="Person")

                # Get all comments on submissions on this group
                comments = self.mongo_db_connector.getCommentsOnSubmission(
                    self.network_name,
                    self.submissions_type,
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
                            network_name=self.network_name,
                            submissions_type=self.submissions_type,
                            comment_id=parent_id
                        )
                        if not parent_comment:
                            continue
                        from_node_id = parent_comment["author_id"]
                        upvotes_weight = parent_comment["upvotes"]

                    interaction_weight = 1
                    activity_weight = 1 + \
                        self.mongo_db_connector.getChildrenCount(
                            self.network_name, self.submissions_type, [comment])

                    # add comment authors as nodes
                    self.addOrUpdateNode(
                        activity_object=comment, node_type="Person")

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
