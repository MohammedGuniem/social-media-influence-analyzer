from classes.statistics.Statistics import Statistics as statistics_methods
from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.modelling.UserGraphModelling import UserGraphModel
from dotenv import load_dotenv
import json
import os

# Reading documents from test .json file.
with open("4_test_case.json", 'r') as model_file:
    test = json.load(model_file)

test_id = test["id"]

# Writing documents to mongoDB.
mongo_db_connector = MongoDBConnector(
    os.environ.get('mongo_connnection_string'))

mongo_db_connector.writeToDB(
    database_name="Subreddits_DB",
    collection_name=test_id,
    data=test["subreddits"]
)

mongo_db_connector.writeToDB(
    database_name=F"{test_id}_Submissions_DB",
    collection_name=test_id,
    data=test["submissions"]
)

mongo_db_connector.writeToDB(
    database_name=F"{test_id}_Comments_DB",
    collection_name=test_id,
    data=test["comments"]
)

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

# Deleting test documents from mongoDB
mongo_db_connector.remove_collection(F"{test_id}_Submissions_DB", test_id)
mongo_db_connector.remove_collection(F"{test_id}_Comments_DB", test_id)
mongo_db_connector.remove_collection("Subreddits_DB", test_id)

expected_edges = test["expected_output"]["user_model"]["edges"]
expected_nodes = test["expected_output"]["user_model"]["nodes"]
if (expected_edges == user_model.edges and expected_nodes == user_model.nodes):
    print("*** User Model Test is Successful! ***")
else:
    print("*** User Model Test is Not Successful! ***")
