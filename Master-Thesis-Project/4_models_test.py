from classes.statistics.Statistics import Statistics as statistics_methods
from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.modelling.EventGraphModelling import EventGraphModel
from classes.modelling.UserGraphModelling import UserGraphModel
from dotenv import load_dotenv
import json
import os

load_dotenv()

# Reading documents from test .json file.
with open("4_models_test_case.json", 'r') as model_file:
    test = json.load(model_file)

test_id = test["id"]

# Writing documents to mongoDB.
mongo_db_connector = MongoDBConnector(
    os.environ.get('mongo_connnection_string'))

for docs in ["Subreddits", "Submissions", "Comments"]:
    mongo_db_connector.writeToDB(
        database_name="Subreddits_DB" if docs == "Subreddits" else F"Test_{docs}_DB",
        collection_name=test_id,
        data=test[docs.lower()]
    )

for model_name in test["expected_output"].keys():
    if model_name == "Event":
        model = EventGraphModel(
            mongodb_connection_string=os.environ.get(
                'mongo_connnection_string'),
            collection_name="Test",
            neo4j_connection_string=os.environ.get('neo4j_connection_string'),
            neo4j_username=os.environ.get('neo4j_username'),
            neo4j_password=os.environ.get('neo4j_password'),
            construct_neo4j_graph=False
        )
    elif model_name == "User":
        model = UserGraphModel(
            mongodb_connection_string=os.environ.get(
                'mongo_connnection_string'),
            collection_name="Test",
            neo4j_connection_string=os.environ.get('neo4j_connection_string'),
            neo4j_username=os.environ.get('neo4j_username'),
            neo4j_password=os.environ.get('neo4j_password'),
            construct_neo4j_graph=False
        )

    print(F"{model_name} Model >> Data feed from: {model.mongo_db_connector.collection_name}")

    print(F"{model_name} Model >> Building model with all possible scoring combinations...")
    model.build_model_for_subreddit_and_type(
        subreddit_display_name=test_id, submission_type=test_id)
    all_edge_weights = model.edges.values()

    print(F"{model_name} Model >> Calculating Summary Statistics for each and every edge scoring combination...")
    model_edge_weights = {}
    for edge_weights in all_edge_weights:
        for k, v in edge_weights.items():
            if k not in model_edge_weights:
                model_edge_weights[k] = []
            model_edge_weights[k].append(v)

    model_statistics = statistics_methods.getSummaryStatistics(
        data_dict=model_edge_weights)

    print(F"{model_name} Model >> Summary statistics of cross validation using 3 different scoring techniques")
    print(model_statistics)

    print(F"{model_name} Model >> Drawing histograms using combinations of 3 different scoring techniques")
    statistics_methods.subplot_histograms(model_edge_weights)

    expected_output = test["expected_output"][model_name]
    expected_edges = expected_output["edges"]
    expected_nodes = expected_output["nodes"]
    if (expected_edges == model.edges and expected_nodes == model.nodes):
        print(F"\n*** {model_name} Model Test is Successful! ***\n")
    else:
        print(F"\n*** {model_name} Model Test is Not Successful! ***\n")


# Deleting test documents from mongoDB
mongo_db_connector.remove_collection(F"{test_id}_Submissions_DB", test_id)
mongo_db_connector.remove_collection(F"{test_id}_Comments_DB", test_id)
mongo_db_connector.remove_collection("Subreddits_DB", test_id)
