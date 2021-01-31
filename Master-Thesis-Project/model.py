from classes.Neo4jConnector import Neo4jConnector
from classes.GraphModelling import GraphModel
from dotenv import load_dotenv
import sys
import os

load_dotenv()

MongoDB_connection_string = os.environ.get('mongo_connnection_string')

graph_model = GraphModel(MongoDB_connection_string)

model_choice = input(
    "Press (1=object flow model), (2=user flow model), (3=merged flow models): ")

# Available crawled subreddits
# Home, AskReddit, Politics
subreddit_display_name = input("Enter subreddit display name: ")

models = []
if model_choice == "1" or model_choice == "3":
    print("Building Subreddit Object Flow Model...")
    object_flow_model = graph_model.buildSubredditObjectFlowModel(
        subreddit_display_name=subreddit_display_name)
    models.append(object_flow_model)
elif model_choice == "2" or model_choice == "3":
    print("Building Subreddit User Flow Model...")
    user_flow_model = graph_model.buildSubredditUserModel(
        subreddit_display_name=subreddit_display_name)
    models.append(user_flow_model)
else:
    sys.exit(0)

neo4j_connector = Neo4jConnector("bolt://localhost:7687", "neo4j", "1234")
for model in models:
    for relation_id, relation_node in model.items():
        neo4j_connector.create_pair(relation_node["FROM"]["type"], relation_node["FROM"]["id"], relation_node["FROM"]["data"],
                                    relation_node["RELATIONSHIP"]["type"], relation_id, relation_node["RELATIONSHIP"]["data"],
                                    relation_node["TO"]["type"], relation_node["TO"]["id"], relation_node["TO"]["data"])
neo4j_connector.close()
