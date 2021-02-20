from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector


class ActionGraphModel:
    def __init__(self, mongodb_connection_string, neo4j_connection_string, neo4j_username, neo4j_password, construct_neo4j_graph):
        # Mongo DB Database Connector
        self.mongo_db_connector = MongoDBConnector(
            mongodb_connection_string
        )

        # Neo4j graph database Connector
        self.graph_db_connector = GraphDBConnector(
            neo4j_connection_string, neo4j_username, neo4j_password)

        self.construct_neo4j_graph = construct_neo4j_graph
        self.nodes = {}
        self.edges = {}

    def addNode(self, activity_object, Type):
        props = {}

        if Type == "Subreddit":
            node_id = activity_object['id']
            props["name"] = activity_object['display_name']
            props["moderators_names"] = []
            props["moderators_ids"] = []
            for moderator in activity_object["moderators"]:
                props["moderators_ids"].append(moderator['id'])
                props["moderators_names"].append(moderator['name'])

        elif Type in ["Submission", "Top_comment", "Sub_comment"]:
            node_id = activity_object["id"]
            props["name"] = activity_object["id"]
            props["author_name"] = activity_object["author_name"]
            props["author_id"] = activity_object["author_id"]

        if not node_id in self.nodes:
            if self.construct_neo4j_graph:
                self.graph_db_connector.addNode(
                    node_id, Type, props)
            self.nodes[node_id] = Type

    def addEdge(self, from_ID, to_ID, score):
        edge_id = F"{from_ID}_{to_ID}"
        if edge_id in self.edges:
            self.edges[edge_id] += score
            score = self.edges[edge_id]
        else:
            self.edges[edge_id] = score

        if self.construct_neo4j_graph:
            self.graph_db_connector.addEdge(
                relation_Type=F"Influences",
                relation_props={"weight": score},
                from_ID=from_ID,
                from_Type=self.nodes[from_ID],
                to_ID=to_ID,
                to_Type=self.nodes[to_ID],
            )

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

            # Draw submission authors
            self.addNode(activity_object=submission, Type="Submission")

            # Get all comments on submissions on this subreddit
            comments = self.mongo_db_connector.getCommentsOnSubmission(
                submission_id,
                submission_type
            )

            submission_score = len(comments) + 1

            for comment in comments:
                comment_id = comment['id']

                parent_id_prefix = comment['parent_id'][0:2]
                parent_id = comment['parent_id'][3:]

                edge_score = 1 + self.get_comment_children_count(
                    [comment], submission_type=submission_type)

                # Comment is top-level
                if parent_id_prefix == "t3":
                    from_node_id = comment["submission_id"][3:]
                    node_type = "Top_comment"

                # Comment is a subcomment
                elif parent_id_prefix == "t1":
                    from_node_id = comment["parent_id"][3:]
                    node_type = "Sub_comment"

                # Draw comment
                self.addNode(activity_object=comment, Type=node_type)

                # Draw edge relation between parent (comment or submission) and child comments.
                self.addEdge(
                    from_ID=from_node_id,
                    to_ID=comment_id,
                    score=edge_score
                )
