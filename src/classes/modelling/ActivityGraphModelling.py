from classes.modelling.GraphModelling import Graph
from classes.modelling.Node import Node
from classes.modelling.Edge import Edge


class ActivityGraph(Graph):
    def __init__(self, mongo_db_connector, neo4j_db_connector, network_name, submissions_type, date):
        self.network_name = network_name
        self.submissions_type = submissions_type
        super().__init__(mongo_db_connector, neo4j_db_connector,
                         network_name, submissions_type, date)

    def addOrUpdateNode(self, activity_object, node_type):
        node_id = activity_object["id"]
        if node_id not in self.nodes:
            node = Node(
                ID=node_id,
                Type=node_type,
                Props={
                    'type': node_type,
                    'network_id': node_id,
                    'name': F"{activity_object['author_name']} ({node_id})",
                    'author_id': activity_object["author_id"],
                    'author_name': activity_object['author_name'],
                    'body': activity_object['body']
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

            # Get all submissions on this subreddit.
            group_id = group_info['id']
            submissions = self.mongo_db_connector.getSubmissionsOnGroup(
                self.network_name, self.submissions_type, group_id)

            for submission in submissions:
                submission_id = submission["id"]

                # add submissions as nodes
                self.addOrUpdateNode(
                    activity_object=submission, node_type="Submission")

                # Get all comments on submissions on this group
                comments = self.mongo_db_connector.getCommentsOnSubmission(
                    self.network_name,
                    self.submissions_type,
                    "t3_"+submission['id']
                )

                submission_body = submission['body']

                for comment in comments:
                    comment_id = comment['id']

                    parent_id_prefix = comment['parent_id'][0:2]
                    parent_id = comment['parent_id'][3:]

                    # Comment is top-level
                    if parent_id_prefix == "t3":
                        node_type = "Top_comment"
                        from_node_id = comment["submission_id"][3:]

                        # Setting the weight to the upvotes score
                        upvotes_weight = submission["upvotes"]

                        # Constructing a document to predict topic
                        topic_document = submission_body + " " + comment['body']

                    # Comment is a subcomment
                    elif parent_id_prefix == "t1":
                        parent_comment = self.mongo_db_connector.getCommentInfo(
                            network_name=self.network_name,
                            submissions_type=self.submissions_type,
                            comment_id=comment["parent_id"][3:]
                        )
                        if not parent_comment:
                            continue
                        node_type = "Sub_comment"
                        from_node_id = parent_comment["id"]

                        # Setting the weight to the upvotes score
                        upvotes_weight = parent_comment["upvotes"]

                        # Constructing a document to predict topic
                        topic_document = submission_body + " " + parent_comment['body'] + " " + comment['body']

                    # add sub-comments as nodes
                    self.addOrUpdateNode(
                        activity_object=comment, node_type=node_type)

                    # Setting the weight of the interaction score and calculating the activity scores
                    interaction_weight = 1
                    activity_weight = 1 + \
                        self.mongo_db_connector.getChildrenCount(
                            self.network_name, self.submissions_type, [comment])

                    # Predicting the topic of influence
                    predicted_influence_area = self.text_classifier.classify_title(topic_document)

                    # Draw edge relation between parent (comment or submission) and child comment.
                    self.addOrUpdateEdge(
                        from_node_id=from_node_id,
                        relation_type="Has",
                        to_node_id=comment_id,
                        influence_area=predicted_influence_area,
                        group_name=group_name,
                        interaction_score=interaction_weight,
                        activity_score=activity_weight,
                        upvotes_score=upvotes_weight
                    )
