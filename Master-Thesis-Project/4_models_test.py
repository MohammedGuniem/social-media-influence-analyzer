from classes.statistics.Statistics import Statistics as statistics_methods
from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from classes.modelling.ActivityGraphModelling import ActivityGraph
from classes.modelling.UserGraphModelling import UserGraph
from dotenv import load_dotenv
from datetime import date
import json
import os

load_dotenv()

mongo_db_connector = MongoDBConnector(
    os.environ.get('mongo_connnection_string'),
    collection_name=test_id
)

neo4j_db_connector = GraphDBConnector(
    uri=os.environ.get('neo4j_connection_string'),
    user=os.environ.get('neo4j_username'),
    password=os.environ.get('neo4j_password'),
)

for model_name in ["usergraph", "activitygraph"]:
    if model_name == "usergraph":
        model = UserGraph(
            mongo_db_connector=mongo_db_connector,
            neo4j_db_connector=neo4j_db_connector
        )
    elif model_name == "activitygraph":
        continue
        model = ActivityGraph(
            mongo_db_connector=mongo_db_connector,
            neo4j_db_connector=neo4j_db_connector
        )

    print(F"{model_name} Model >> Data feed from: {model.mongo_db_connector.collection_name}")

    print(F"{model_name} Model >> Building model with all possible scoring combinations...")
    for display_name in subreddits_display_names:
        model.build_model(subreddit_display_name=display_name,
                          submission_type="New")

    database_name = F"{test_id}{model_name}{str(date.today()).replace('-','')}"
    model.save(database_name)

    def extract_score(edge_props):
        return {'connection_influence_score': edge_props['connection_influence_score'],
                'activity_influence_score': edge_props['activity_influence_score'],
                'upvotes_influence_score': edge_props['upvotes_influence_score'],
                'connection_and_activity_influence_score': edge_props['connection_and_activity_influence_score'],
                'connection_and_upvotes_influence_score': edge_props['connection_and_upvotes_influence_score'],
                'activity_and_upvotes_influence_score': edge_props['activity_and_upvotes_influence_score'],
                'all_influence_score': edge_props['all_influence_score']}

    print(F"{model_name} Model >> Calculating Summary Statistics for each and every edge scoring combination...")
    all_edge_weights = []
    for edge in model.edges.values():
        scores = extract_score(edge['props'])
        all_edge_weights.append(scores)

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

# Deleting test documents from mongoDB
mongo_db_connector.remove_collection(F"{test_id}_Submissions_DB", test_id)
mongo_db_connector.remove_collection(F"{test_id}_Comments_DB", test_id)
mongo_db_connector.remove_collection("Subreddits_DB", test_id)
