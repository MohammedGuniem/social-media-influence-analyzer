from classes.Neo4jConnector import Neo4jConnector
from classes.GraphModelling import GraphModel
from dotenv import load_dotenv
import os

load_dotenv()

MongoDB_connection_string = os.environ.get('mongo_connnection_string')

graph_model = GraphModel("Model A", MongoDB_connection_string)


# Available crawled subreddits
# Home, AskReddit, Politics

graph_model.buildUserModel("AskReddit", moderator_weight=1,
                           submission_author_weight=1, parent_comment_author_weight=1)

#model = graph_model.buildSubredditFlowModel(subreddit_display_name="Home")

neo4j_connector = Neo4jConnector("bolt://localhost:7687", "neo4j", "1234")

for relation_id, relation_node in model.items():
    neo4j_connector.create_pair(relation_node["FROM"]["type"], relation_node["FROM"]["id"], relation_node["FROM"]["data"],
                                relation_node["RELATIONSHIP"]["type"], relation_id, relation_node["RELATIONSHIP"]["data"],
                                relation_node["TO"]["type"], relation_node["TO"]["id"], relation_node["TO"]["data"])

neo4j_connector.close()
