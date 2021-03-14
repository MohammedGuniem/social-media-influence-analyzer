from classes.modelling.TextClassification import TextClassifier


class Graph:
    def __init__(self, mongo_db_connector, neo4j_db_connector):
        self.mongo_db_connector = mongo_db_connector
        self.neo4j_db_connector = neo4j_db_connector
        self.text_classifier = TextClassifier(mongo_db_connector)
        self.nodes = {}
        self.edges = {}

    def extract_score(self, edge_props):
        return {'connection_influence_score': edge_props['connection_influence_score'],
                'activity_influence_score': edge_props['activity_influence_score'],
                'upvotes_influence_score': edge_props['upvotes_influence_score'],
                'connection_and_activity_influence_score': edge_props['connection_and_activity_influence_score'],
                'connection_and_upvotes_influence_score': edge_props['connection_and_upvotes_influence_score'],
                'activity_and_upvotes_influence_score': edge_props['activity_and_upvotes_influence_score'],
                'all_influence_score': edge_props['all_influence_score']}

    def get_edge_scores(self, connection_weight, activity_weight, upvotes_weight):
        edge_scores = {
            "connection_influence_score": connection_weight,
            "activity_influence_score": activity_weight,
            "upvotes_influence_score": upvotes_weight,
            "connection_and_activity_influence_score":  connection_weight + activity_weight,
            "connection_and_upvotes_influence_score": connection_weight + upvotes_weight,
            "activity_and_upvotes_influence_score": activity_weight + upvotes_weight,
            "all_influence_score": connection_weight + activity_weight + upvotes_weight
        }
        return edge_scores

    def build_graph(self, submissions_types):
        self.nodes = {}
        self.edges = {}
        subreddits = self.mongo_db_connector.getSubredditsInfo()

        for submissions_type in submissions_types:
            for subreddit in subreddits:
                self.build_model(
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
