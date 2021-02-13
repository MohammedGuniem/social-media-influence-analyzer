from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from classes.modelling.ActionGraphModelling import ActionGraphModel
from classes.modelling.UserGraphModelling import UserGraphModel
from dotenv import load_dotenv
import sys
import os

# Loading Enviroment variables
load_dotenv()
MongoDB_connection_string = os.environ.get('mongo_connnection_string')

# Database connectors
mongo_db_connector = MongoDBConnector(MongoDB_connection_string)
graph_db_connector = GraphDBConnector("bolt://localhost:7687", "neo4j", "1234")

user_choice = input(
    "Enter (U) for User Model, (A) for Action Model, (*) for both and (0 or any other key) to exit:").upper()
if user_choice == "U":
    graph_model = UserGraphModel(mongo_db_connector, graph_db_connector)
elif user_choice == "A":
    graph_model = ActionGraphModel(mongo_db_connector, graph_db_connector)
elif user_choice == "*":
    print("Making mixed/hyper graph...")
else:
    sys.exit(0)

subreddits = mongo_db_connector.getSubredditsInfo()
submissions_types = ["New", "Rising"]

for submissions_type in submissions_types:
    for subreddit in subreddits:
        graph_model.buildModel(
            subreddit_display_name=subreddit["display_name"],
            submission_type=submissions_type
        )
