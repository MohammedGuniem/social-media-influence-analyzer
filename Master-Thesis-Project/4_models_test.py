from classes.statistics.Statistics import Statistics as statistics_methods
from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from classes.modelling.ActivityGraphModelling import ActivityGraphModel
from classes.modelling.UserGraphModelling import UserGraphModel
from dotenv import load_dotenv
from datetime import date
import json
import os

load_dotenv()

# Reading documents from test .json file.
with open("4_models_test_case.json", 'r') as model_file:
    test = json.load(model_file)

test_id = test["id"]

# Writing documents to mongoDB.
mongo_db_connector = MongoDBConnector(
    os.environ.get('mongo_connnection_string'),
    collection_name=test_id
)

for docs in ["Subreddits", "Submissions", "Comments"]:
    mongo_db_connector.writeToDB(
        database_name="Subreddits_DB" if docs == "Subreddits" else F"Test_{docs}_DB",
        collection_name=test_id,
        data=test[docs.lower()]
    )

# Making a neo4j graph connector
neo4j_db_connector = GraphDBConnector(
    uri=os.environ.get('neo4j_connection_string'),
    user=os.environ.get('neo4j_username'),
    password=os.environ.get('neo4j_password'),
)

for model_name in test["expected_output"].keys():
    if model_name == "activities":
        model = ActivityGraphModel(
            mongo_db_connector=mongo_db_connector,
            neo4j_db_connector=neo4j_db_connector
        )
    elif model_name == "users":
        model = UserGraphModel(
            mongo_db_connector=mongo_db_connector,
            neo4j_db_connector=neo4j_db_connector
        )
    else:
        import sys
        sys.exit(0)

    print(F"{model_name} Model >> Data feed from: {model.mongo_db_connector.collection_name}")

    print(F"{model_name} Model >> Building model with all possible scoring combinations...")
    model.build_model_for_subreddit_and_type(
        subreddit_display_name=test_id, submission_type=test_id)

    database_name = F"{test_id}{model_name}{str(date.today()).replace('-','')}"
    model.save(database_name)

    print(F"{model_name} Model >> Calculating Summary Statistics for each and every edge scoring combination...")
    all_edge_weights = []
    for edge in model.edges.values():
        all_edge_weights.append(edge['props'])

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

    successful_test = True
    for edge_id, edge in model.edges.items():
        if edge["props"] != expected_edges[edge_id]:
            successful_test = False
            print("----- Expected edge ----->")
            print(edge["props"])
            print("----- Got edge ----->")
            print(expected_edges[edge_id])
            break

    for node_id, node in model.nodes.items():
        if node["type"] != expected_nodes[node_id]:
            successful_test = False
            print("----- Expected edge ----->")
            print(edge["props"])
            print("----- Got edge ----->")
            print(expected_edges[edge_id])
            break

    if (successful_test):
        print(F"\n*** {model_name} Model Test is Successful! ***\n")
    else:
        print(F"\n*** {model_name} Model Test is Not Successful! ***\n")

# Deleting test documents from mongoDB
mongo_db_connector.remove_collection(F"{test_id}_Submissions_DB", test_id)
mongo_db_connector.remove_collection(F"{test_id}_Comments_DB", test_id)
mongo_db_connector.remove_collection("Subreddits_DB", test_id)
