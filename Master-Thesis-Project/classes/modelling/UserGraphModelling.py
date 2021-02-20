from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector


class UserGraphModel:
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
                to_Type=self.nodes[to_ID]
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

    def buildModelForSubredditAndType(self, subreddit_display_name, submission_type, connection_count_score, activity_weight_score, upvotes_count_score):
        # Get subreddit information.
        subreddit = self.mongo_db_connector.getSubredditInfo(
            subreddit_display_name)

        # Get all submissions on this subreddit.
        subreddit_id = subreddit['id']
        submissions = self.mongo_db_connector.getSubmissionsOnSubreddit(
            subreddit_id, submission_type)

        for submission in submissions:
            submission_author_id = submission["author_id"]

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

                score = 1 if connection_count_score else 0
                score += self.get_comment_children_count(
                    comments_array=[comment], submission_type=submission_type) if activity_weight_score else 0

                # Comment is top-level
                if parent_id_prefix == "t3":

                    score += submission["upvotes"] if upvotes_count_score else 0

                    # Draw influence relation between submission author and top-level commenters
                    self.addEdge(
                        from_ID=submission_author_id,
                        to_ID=comment_author_id,
                        score=score
                    )

                # Comment is a thread comment
                elif parent_id_prefix == "t1":

                    score += comment["upvotes"] if upvotes_count_score else 0

                    parent_comment = self.mongo_db_connector.getCommentInfo(
                        comment_id=parent_id,
                        Type=submission_type
                    )

                    if parent_comment:
                        # Draw influence relation between parent commenters and child commenters
                        self.addEdge(
                            from_ID=parent_comment["author_id"],
                            to_ID=comment_author_id,
                            score=score
                        )

    def buildModel(self, add_connection_count=False, add_activity_weight=False, add_upvotes_count=False):
        self.nodes = {}
        self.edges = {}
        subreddits = self.mongo_db_connector.getSubredditsInfo()
        submissions_types = ["New", "Rising"]

        for submissions_type in submissions_types:
            for subreddit in subreddits:
                self.buildModelForSubredditAndType(
                    subreddit_display_name=subreddit["display_name"],
                    submission_type=submissions_type,
                    connection_count_score=add_connection_count,
                    activity_weight_score=add_activity_weight,
                    upvotes_count_score=add_upvotes_count)
