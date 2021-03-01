from classes.modelling.GraphModelling import Graph


class UserGraph(Graph):
    def __init__(self, mongo_db_connector, neo4j_db_connector):
        super().__init__(mongo_db_connector, neo4j_db_connector)

    def add_node(self, activity_object, node_type):
        node_id = activity_object["author_id"]
        node = {
            'id': node_id,
            'type': node_type,
            "props": {
                'network_id': node_id,
                'name': activity_object['author_name'],
                'author_id': activity_object["author_id"]
            }
        }
        self.nodes[node_id] = node

    def add_edge(self, from_node_id, relation_type, to_node_id, scores):
        edge_props = {}
        edge_id = F"{from_node_id}_{relation_type}_{to_node_id}"
        if edge_id in self.edges:
            updated_scores = self.update_score(
                current_scores=self.edges[edge_id]['props'],
                add_scores=scores
            )
        else:
            updated_scores = scores

        edge = {
            'id': edge_id,
            'type': relation_type,
            'from_node_id': from_node_id,
            'to_node_id': to_node_id,
            'props': updated_scores
        }
        self.edges[edge_id] = edge

    def update_score(self, current_scores, add_scores):
        for key_score, weight in current_scores.items():
            current_scores[key_score] += add_scores[key_score]
        return current_scores

    def build_model(self, subreddit_display_name, submission_type):
        # Get subreddit information.
        subreddit = self.mongo_db_connector.getSubredditInfo(
            subreddit_display_name)

        # Get all submissions on this subreddit.
        subreddit_id = subreddit['id']
        submissions = self.mongo_db_connector.getSubmissionsOnSubreddit(
            subreddit_id, submission_type)

        for submission in submissions:
            # add submission authors as nodes
            self.add_node(activity_object=submission, node_type="Redditor")

            # Get all comments on submissions on this subreddit
            comments = self.mongo_db_connector.getCommentsOnSubmission(
                submission['id'],
                submission_type
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
                        comment_id=parent_id,
                        Type=submission_type
                    )
                    if not parent_comment:
                        continue
                    from_node_id = parent_comment["author_id"]
                    upvotes_weight = parent_comment["upvotes"]

                connection_weight = 1
                activity_weight = 1 + self.mongo_db_connector.get_children_count(
                    [comment], submission_type=submission_type)

                # Get scores
                edge_scores = self.get_edge_scores(
                    connection_weight, activity_weight, upvotes_weight)

                # add comment authors as nodes
                self.add_node(activity_object=comment, node_type="Redditor")

                # Draw influence relation between authors/commenters and child commenters
                self.add_edge(
                    from_node_id=from_node_id,
                    relation_type="Influences",
                    to_node_id=comment_author_id,
                    scores=edge_scores,
                )
