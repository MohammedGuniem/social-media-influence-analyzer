from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector


class UserGraphModel:
    def __init__(self, mongodb_connection_string, neo4j_connection_string, neo4j_username, neo4j_password, construct_neo4j_graph, collection_name=None):

        # Mongo DB Database Connector
        self.mongo_db_connector = MongoDBConnector(
            mongodb_connection_string,
            collection_name=collection_name
        )

        # Neo4j graph database Connector
        if construct_neo4j_graph:
            self.graph_db_connector = GraphDBConnector(
                neo4j_connection_string, neo4j_username, neo4j_password)

        self.construct_neo4j_graph = construct_neo4j_graph
        self.nodes = {}
        self.edges = {}

    def addNode(self, activity_object, Type):
        props = {}

        if Type == "Redditor":
            node_id = activity_object["author_id"]
            props["name"] = activity_object["author_name"]

        elif Type == "Subreddit":
            node_id = activity_object['id']
            props["name"] = activity_object['display_name']
            props["moderators_names"] = []
            props["moderators_ids"] = []
            for moderator in activity_object["moderators"]:
                props["moderators_ids"].append(moderator['id'])
                props["moderators_names"].append(moderator['name'])

        if not node_id in self.nodes:
            if self.construct_neo4j_graph:
                self.graph_db_connector.addNode(node_id, Type, props)
            self.nodes[node_id] = Type

    def addEdge(self, from_ID, to_ID, scores):
        edge_id = F"{from_ID}_{to_ID}"
        if edge_id in self.edges:
            updated_scores = self.update_score(
                self.edges[edge_id],
                scores
            )
            self.edges[edge_id] = updated_scores
        else:
            self.edges[edge_id] = scores

        scores = self.edges[edge_id]
        if self.construct_neo4j_graph:
            self.graph_db_connector.addEdge(
                relation_Type=F"Influences",
                relation_props=scores,
                from_ID=from_ID,
                from_Type=self.nodes[from_ID],
                to_ID=to_ID,
                to_Type=self.nodes[to_ID]
            )

    def get_edge_scores(self, connection_weight, event_weight, upvotes_weight):
        edge_scores = {
            "connection": connection_weight,
            "event": event_weight,
            "upvotes": upvotes_weight,
            "connection_and_event":  connection_weight + event_weight,
            "connection_and_upvotes": connection_weight + upvotes_weight,
            "event_and_upvotes": event_weight + upvotes_weight,
            "all": connection_weight + event_weight + upvotes_weight
        }
        return edge_scores

    def update_score(self, current_scores, add_scores):
        for key_score, weight in current_scores.items():
            current_scores[key_score] += add_scores[key_score]
        return current_scores

    def get_comment_children_count(self, comments_array, submission_type):
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
            score = sum(children_of_children_num) + self.get_comment_children_count(
                comments_array=children_array, submission_type=submission_type)
        return score

    def build_model_for_subreddit_and_type(self, subreddit_display_name, submission_type):
        # Get subreddit information.
        subreddit = self.mongo_db_connector.getSubredditInfo(
            subreddit_display_name)

        # Get all submissions on this subreddit.
        subreddit_id = subreddit['id']
        submissions = self.mongo_db_connector.getSubmissionsOnSubreddit(
            subreddit_id, submission_type)

        for submission in submissions:
            # Draw submission authors
            self.addNode(activity_object=submission, Type="Redditor")

            # Get all comments on submissions on this subreddit
            comments = self.mongo_db_connector.getCommentsOnSubmission(
                submission['id'],
                submission_type
            )

            for comment in comments:
                comment_author_id = comment['author_id']

                # Draw commenters
                self.addNode(activity_object=comment, Type="Redditor")

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
                    from_node_id = parent_comment["author_id"]
                    upvotes_weight = parent_comment["upvotes"]

                connection_weight = 1
                event_weight = 1 + self.get_comment_children_count(
                    [comment], submission_type=submission_type)

                # Get scores
                edge_scores = self.get_edge_scores(
                    connection_weight, event_weight, upvotes_weight)

                # Draw influence relation between authors/commenters and child commenters
                self.addEdge(
                    from_ID=from_node_id,
                    to_ID=comment_author_id,
                    scores=edge_scores
                )

    def buildModel(self):
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
