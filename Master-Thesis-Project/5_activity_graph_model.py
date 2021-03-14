from classes.statistics.Statistics import Statistics as statistics_methods
from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from classes.modelling.ActivityGraphModelling import ActivityGraph
from dotenv import load_dotenv
from datetime import date
import json
import os

load_dotenv()

# Making a mongo db graph connector
mongo_db_connector = MongoDBConnector(
    os.environ.get('mongo_connnection_string')
)

# Making a neo4j graph connector
neo4j_db_connector = GraphDBConnector(
    uri=os.environ.get('neo4j_connection_string'),
    user=os.environ.get('neo4j_username'),
    password=os.environ.get('neo4j_password'),
)

model = ActivityGraph(
    mongo_db_connector=mongo_db_connector,
    neo4j_db_connector=neo4j_db_connector
)

print(
    F"Activity Graph Model >> Data feed from: {model.mongo_db_connector.collection_name}")

print("Activity Graph Model >> Building model with all possible scoring combinations...")
model.build_graph(submissions_types=["Rising"])

database_name = F"activitygraph{str(date.today()).replace('-','')}"
model.save(database_name)

print("Activity Graph Model >> Calculating Summary Statistics for each and every edge scoring combination...")
all_edge_weights = []
for edge in model.edges.values():
    scores = model.extract_score(edge['props'])
    all_edge_weights.append(scores)

model_edge_weights = {}
for edge_weights in all_edge_weights:
    for k, v in edge_weights.items():
        if k not in model_edge_weights:
            model_edge_weights[k] = []
        model_edge_weights[k].append(v)

model_statistics = statistics_methods.getSummaryStatistics(
    data_dict=model_edge_weights)

print("Activity Graph Model >> Summary statistics of cross validation using 3 different scoring techniques")
print(model_statistics)

print(F"Activity Graph Model >> Drawing histograms using combinations of 3 different scoring techniques")
statistics_methods.subplot_histograms(model_edge_weights)

mongo_db_connector.logg_reading_runtimes()
