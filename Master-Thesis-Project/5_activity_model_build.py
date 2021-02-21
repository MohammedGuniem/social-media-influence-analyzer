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

print("building Event Graph model without any edge weight...")
# u - Event Graph model without any edge weight
event_model.build_model()
u_edge_weights = event_model.edges.values()

# uc - Event Graph model with connection score only
print("building Event Graph model with connection score only...")
event_model.build_model(add_connection_count=True)
uc_edge_weights = event_model.edges.values()

print("building Event Graph model with activity score only...")
# ua - Event Graph model with activity score only
event_model.build_model(add_activity_weight=True)
ua_edge_weights = event_model.edges.values()

print("building Event Graph model with upvote score only")
# uu - Event Graph model with upvote score only
event_model.build_model(add_upvotes_count=True)
uu_edge_weights = event_model.edges.values()

print("building Event Graph model with connection and activity scores...")
# uca - Event Graph model with connection and activity scores
event_model.build_model(add_connection_count=True, add_activity_weight=True)
uca_edge_weights = event_model.edges.values()

print("building Event Graph model with connection and upvote scores...")
# uca - Event Graph model with connection and upvote scores
event_model.build_model(add_connection_count=True, add_upvotes_count=True)
ucu_edge_weights = event_model.edges.values()

print("building Event Graph model with activity and upvote scores...")
# uau - Event Graph model with activity and upvote scores
event_model.build_model(add_activity_weight=True, add_upvotes_count=True)
uau_edge_weights = event_model.edges.values()

print("building Event Graph model with connection, activity and upvote scores...")
# ucau - Event Graph model with connection, activity and upvote scores
event_model.build_model(add_connection_count=True,
                        add_upvotes_count=True, add_activity_weight=True)
ucau_edge_weights = event_model.edges.values()

print("Calculating Summary Statistics...")
event_models_edge_weights = {
    'no score': u_edge_weights,
    'connection': uc_edge_weights,
    'activity': ua_edge_weights,
    'upvotes': uu_edge_weights,
    'connection+activity': uca_edge_weights,
    'connection+upvotes': ucu_edge_weights,
    'activity+upvotes': uau_edge_weights,
    'connection+activity+upvotes': ucau_edge_weights
}

event_models_statistics = statistics_methods.getSummaryStatistics(
    data_dict=event_models_edge_weights)

print("Summary statistics cross validation for event graph models")
print("using 3 different scoring techniques for user relations")
print(event_models_statistics)

event_model.mongo_db_connector.logg_reading_runtimes()
