from classes.modelling.GraphModelling import Graph


class ActivityGraph(Graph):
    def __init__(self, mongo_db_connector, neo4j_db_connector):
        super().__init__(mongo_db_connector, neo4j_db_connector)

    def add_node(self, activity_object, node_type):
        node_id = activity_object['id']
        node = {
            'id': node_id,
            'type': node_type,
            "props": {
                'network_id': node_id,
                'name': F"{activity_object['author_name']} ({activity_object['id']})",
                'author_name': activity_object['author_name'],
                'author_id': activity_object["author_id"]
            }
        }
        self.nodes[node_id] = node

    def add_edge(self, from_node_id, relation_type, to_node_id, scores, influence_areas):
        edge_id = F"{from_node_id}_{relation_type}_{to_node_id}"
        edge = {
            'id': edge_id,
            'type': relation_type,
            'from_node_id': from_node_id,
            'to_node_id': to_node_id,
            'props': {
                "influence_scores": scores,
                "influence_areas": influence_areas
            }
        }
        self.edges[edge_id] = edge

    def build_model(self, subreddit_display_name, submission_type):
        # Get subreddit information.
        subreddit = self.mongo_db_connector.getSubredditInfo(
            subreddit_display_name)

        # Get all submissions on this subreddit.
        subreddit_id = subreddit['id']
        submissions = self.mongo_db_connector.getSubmissionsOnSubreddit(
            subreddit_id, submission_type)

        for submission in submissions:
            submission_id = submission["id"]

            # add submissions as nodes
            self.add_node(activity_object=submission, node_type="Submission")

            # Get all comments on submissions from this subreddit
            comments = self.mongo_db_connector.getCommentsOnSubmission(
                submission_id,
                submission_type
            )

            for comment in comments:
                comment_id = comment['id']

                parent_id_prefix = comment['parent_id'][0:2]
                parent_id = comment['parent_id'][3:]

                # Comment is top-level
                if parent_id_prefix == "t3":
                    from_node_id = comment["submission_id"][3:]
                    node_type = "Top_comment"
                    upvotes_weight = submission["upvotes"]

                # Comment is a subcomment
                elif parent_id_prefix == "t1":
                    node_type = "Sub_comment"
                    parent_comment = self.mongo_db_connector.getCommentInfo(
                        comment_id=comment["parent_id"][3:],
                        Type=submission_type
                    )
                    from_node_id = parent_comment["id"]
                    upvotes_weight = parent_comment["upvotes"]

                connection_weight = 1
                activity_weight = 1 + self.mongo_db_connector.get_children_count(
                    [comment], submission_type=submission_type)

                # Get scores
                edge_scores = self.get_edge_scores(
                    connection_weight, activity_weight, upvotes_weight)

                # add comments as nodes
                to_node = self.add_node(
                    activity_object=comment, node_type=node_type)

                # Draw edge relation between parent (comment or submission) and child comments.
                self.add_edge(
                    from_node_id=from_node_id,
                    relation_type="Got",
                    to_node_id=comment_id,
                    scores=edge_scores,
                    influence_areas=["comedy", "sports", "politics"]
                )
