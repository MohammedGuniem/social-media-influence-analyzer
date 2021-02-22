from classes.statistics.Statistics import Statistics as statistics_methods
from classes.modelling.UserGraphModelling import UserGraphModel
from dotenv import load_dotenv
import os

# Loading Enviroment variables and initiating a user graph model instance
load_dotenv()
user_model = UserGraphModel(
    mongodb_connection_string=os.environ.get('mongo_connnection_string'),
    collection_name="Test",
    neo4j_connection_string=os.environ.get('neo4j_connection_string'),
    neo4j_username=os.environ.get('neo4j_username'),
    neo4j_password=os.environ.get('neo4j_password'),
    construct_neo4j_graph=False
)

print(F"Data feed from: {user_model.mongo_db_connector.collection_name}")

print("building User Graph model with all possible scoring combinations...")
user_model.build_model_for_subreddit_and_type(
    subreddit_display_name="Test", submission_type="Test")
all_edge_weights = user_model.edges.values()

print("Calculating Summary Statistics for each and every edge scoring combination...")
user_model_edge_weights = {}
for edge_weights in all_edge_weights:
    for k, v in edge_weights.items():
        if k not in user_model_edge_weights:
            user_model_edge_weights[k] = []
        user_model_edge_weights[k].append(v)

user_models_statistics = statistics_methods.getSummaryStatistics(
    data_dict=user_model_edge_weights)

print("Summary statistics cross validation for user graph models")
print("using 3 different scoring techniques for user relations")
print(user_models_statistics)

user_model.mongo_db_connector.logg_reading_runtimes()
