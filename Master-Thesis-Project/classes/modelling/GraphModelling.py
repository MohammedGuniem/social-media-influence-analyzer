class Graph:
    def __init__(self, mongo_db_connector, neo4j_db_connector):
        self.mongo_db_connector = mongo_db_connector
        self.neo4j_db_connector = neo4j_db_connector
        self.nodes = {}
        self.edges = {}

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
