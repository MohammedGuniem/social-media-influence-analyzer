from classes.modelling.UserGraphModelling import UserGraphModel
from classes.statistics.Statistics import Statistics as statistics_methods
from dotenv import load_dotenv
import os

# Loading Enviroment variables and initiating a user graph model instance
load_dotenv()
user_model = UserGraphModel(
    mongodb_connection_string=os.environ.get('mongo_connnection_string'),
    neo4j_connection_string=os.environ.get('neo4j_connection_string'),
    neo4j_username=os.environ.get('neo4j_username'),
    neo4j_password=os.environ.get('neo4j_password'),
    construct_neo4j_graph=False
)

print(F"Data feed from: {user_model.mongo_db_connector.collection_name}")

print("building User Graph model without any edge weight...")
# u - User Graph model without any edge weight
user_model.buildModel()
u_edge_weights = user_model.edges.values()

# uc - User Graph model with connection score only
print("building User Graph model with connection score only...")
user_model.buildModel(add_connection_count=True)
uc_edge_weights = user_model.edges.values()

print("building User Graph model with activity score only...")
# ua - User Graph model with activity score only
user_model.buildModel(add_activity_weight=True)
ua_edge_weights = user_model.edges.values()

print("building User Graph model with upvote score only")
# uu - User Graph model with upvote score only
user_model.buildModel(add_upvotes_count=True)
uu_edge_weights = user_model.edges.values()

print("building User Graph model with connection and activity scores...")
# uca - User Graph model with connection and activity scores
user_model.buildModel(add_connection_count=True, add_activity_weight=True)
uca_edge_weights = user_model.edges.values()

print("building User Graph model with connection and upvote scores...")
# uca - User Graph model with connection and upvote scores
user_model.buildModel(add_connection_count=True, add_upvotes_count=True)
ucu_edge_weights = user_model.edges.values()

print("building User Graph model with activity and upvote scores...")
# uau - User Graph model with activity and upvote scores
user_model.buildModel(add_activity_weight=True, add_upvotes_count=True)
uau_edge_weights = user_model.edges.values()

print("building User Graph model with connection, activity and upvote scores...")
# ucau - User Graph model with connection, activity and upvote scores
user_model.buildModel(add_connection_count=True,
                      add_upvotes_count=True, add_activity_weight=True)
ucau_edge_weights = user_model.edges.values()

print("Calculating Summary Statistics...")
user_models_edge_weights = {
    'no score': u_edge_weights,
    'connection': uc_edge_weights,
    'activity': ua_edge_weights,
    'upvotes': uu_edge_weights,
    'connection+activity': uca_edge_weights,
    'connection+upvotes': ucu_edge_weights,
    'activity+upvotes': uau_edge_weights,
    'connection+activity+upvotes': ucau_edge_weights
}

user_models_statistics = statistics_methods.getSummaryStatistics(
    data_dict=user_models_edge_weights)

print("Summary statistics cross validation for user graph models")
print("using 3 different scoring techniques for user relations")
print(user_models_statistics)

user_model.mongo_db_connector.logg_reading_runtimes()

"""
# Action Graph model
action_graph_model = ActionGraphModel(mongo_db_connector, graph_db_connector)
action_graph_model.buildModel()
action_edge_weights = action_graph_model.edges.values()

action_model_edge_weights_df = pd.DataFrame({
    'Action Model': action_edge_weights
})
action_model_statistics = getSummaryStatistics(df=action_model_edge_weights_df)
print(action_model_statistics)
"""

"""
print("user graph model values count")
l = list(user_graph_model.edges.values())
for i in sorted(set(l)):
    print(F"value: {i}, count: {l.count(i)}")

print("action graph model values count")
l = list(action_graph_model.edges.values())
for i in sorted(set(l)):
    print(F"value: {i}, count: {l.count(i)}")

print("combined graph model values count")
l = list(combined_graph_model.edges.values())
for i in sorted(set(l)):
    print(F"value: {i}, count: {l.count(i)}")
"""
