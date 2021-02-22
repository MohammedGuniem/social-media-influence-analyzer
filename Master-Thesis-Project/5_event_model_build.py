from classes.modelling.EventGraphModelling import EventGraphModel
from classes.statistics.Statistics import Statistics as statistics_methods
from dotenv import load_dotenv
import os

# Loading Enviroment variables and initiating a user graph model instance
load_dotenv()
event_model = EventGraphModel(
    mongodb_connection_string=os.environ.get('mongo_connnection_string'),
    neo4j_connection_string=os.environ.get('neo4j_connection_string'),
    neo4j_username=os.environ.get('neo4j_username'),
    neo4j_password=os.environ.get('neo4j_password'),
    construct_neo4j_graph=False
)

print(F"Data feed from: {event_model.mongo_db_connector.collection_name}")

print("building Event Graph model with all possible scoring combinations...")
event_model.build_model()
all_edge_weights = event_model.edges.values()

print("Calculating Summary Statistics for each and every edge scoring combination...")
event_model_edge_weights = {}
for edge_weights in all_edge_weights:
    for k, v in edge_weights.items():
        if k not in event_model_edge_weights:
            event_model_edge_weights[k] = []
        event_model_edge_weights[k].append(v)

event_models_statistics = statistics_methods.getSummaryStatistics(
    data_dict=event_model_edge_weights)

print("Summary statistics cross validation for event graph models")
print("using 3 different scoring techniques for event relations")
print(event_models_statistics)

event_model.mongo_db_connector.logg_reading_runtimes()

print("Drawing histograms for user graph models")
print("using 3 different scoring techniques for user relations")
