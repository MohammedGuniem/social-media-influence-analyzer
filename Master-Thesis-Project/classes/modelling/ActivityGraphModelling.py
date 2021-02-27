class ActivityGraphModel:
    def __init__(self, mongo_db_connector, neo4j_db_connector):
        self.mongo_db_connector = mongo_db_connector
        self.neo4j_db_connector = neo4j_db_connector
        self.nodes = {}
        self.edges = {}

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

    def add_edge(self, from_node_id, relation_type, to_node_id, scores):
        edge_id = F"{from_node_id}_{relation_type}_{to_node_id}"
        edge = {
            'id': edge_id,
            'type': relation_type,
            'from_node_id': from_node_id,
            'to_node_id': to_node_id,
            'props': scores
        }
        self.edges[edge_id] = edge

    def get_children_count(self, comments_array, submission_type):
        children_array = []
        children_of_children_num = []
        for comment in comments_array:
            children = self.mongo_db_connector.getCommentChildren(
                comment_id=comment['id'], Type=submission_type)

            children_array += children
            children_of_children_num.append(len(children))

        if sum(children_of_children_num) == 0:
            return 0
        else:
            score = sum(children_of_children_num) + self.get_children_count(
                comments_array=children_array, submission_type=submission_type)
        return score

    def get_edge_scores(self, connection_weight, activity_weight, upvotes_weight):
        edge_scores = {
            "connection": connection_weight,
            "activity": activity_weight,
            "upvotes": upvotes_weight,
            "connection_and_activity":  connection_weight + activity_weight,
            "connection_and_upvotes": connection_weight + upvotes_weight,
            "activity_and_upvotes": activity_weight + upvotes_weight,
            "all": connection_weight + activity_weight + upvotes_weight
        }
        return edge_scores

    def build_model_for_subreddit_and_type(self, subreddit_display_name, submission_type):
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

                    activity_weight = 1 + self.get_children_count(
                        [comment], submission_type=submission_type)
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
                activity_weight = 1 + self.get_children_count(
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
                    scores=edge_scores
                )

    def build_model(self):
        self.nodes = {}
        self.edges = {}
        subreddits = self.mongo_db_connector.getSubredditsInfo()
        submissions_types = ["New"]

        for submissions_type in submissions_types:
            for subreddit in subreddits:
                self.build_model_for_subreddit_and_type(
                    subreddit_display_name=subreddit["display_name"],
                    submission_type=submissions_type
                )

    def save(self, database_name):
        # Create or clear/replace database
        self.neo4j_db_connector.set_database(database_name)

        # Saving nodes in neo4j database graph.
        for node_id, node in self.nodes.items():
            self.neo4j_db_connector.save_node(
                node_id, node['type'], node['props']
            )

        # Saving edges in neo4j database graph.
        for edge_id, edge in self.edges.items():
            self.neo4j_db_connector.save_edge(
                from_node=self.nodes[edge['from_node_id']],
                to_node=self.nodes[edge['to_node_id']],
                edge_type=edge['type'],
                edge_props=edge['props']
            )
