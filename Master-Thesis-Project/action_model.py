from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from classes.modelling.ActionGraphModelling import ActionGraphModel

from dotenv import load_dotenv
import os

# Enviroment variables
load_dotenv()
MongoDB_connection_string = os.environ.get('mongo_connnection_string')

# Database connectors
mongo_db_connector = MongoDBConnector(MongoDB_connection_string)
graph_db_connector = GraphDBConnector("bolt://localhost:7687", "neo4j", "1234")

user_graph_model = ActionGraphModel(mongo_db_connector, graph_db_connector)

subreddits = mongo_db_connector.getSubredditsInfo()
subreddits = [subreddits[1]]
submissions_types = ["Rising"]  # , "New"]

for submissions_type in submissions_types:
    for subreddit in subreddits:
        user_graph_model.buildModel(
            subreddit_display_name=subreddit["display_name"],
            submission_type=submissions_type
        )
