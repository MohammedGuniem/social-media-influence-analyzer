from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from classes.modelling.ActionGraphModelling import ActionGraphModel
from classes.modelling.UserGraphModelling import UserGraphModel
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import os

# Loading Enviroment variables
load_dotenv()
MongoDB_connection_string = os.environ.get('mongo_connnection_string')

# Database connectors
mongo_db_connector = MongoDBConnector(MongoDB_connection_string)
graph_db_connector = GraphDBConnector("bolt://localhost:7687", "neo4j", "1234")


def getSummaryStatistics(df):
    # Rename '50%' percentile to '50% - median' since it is the same.
    summary_statistics = df.describe(
        percentiles=[0.1, 0.25, 0.5, 0.75, 0.9]).rename(index={'50%': '50% - median'})

    # Calculate mode and append to statistics dataframe.
    mode_statistics = df.mode().rename(index={0: 'mode'}).iloc[0]
    summary_statistics = summary_statistics.append(mode_statistics)

    # Calculate variance and append to statistics dataframe.
    var_statistics = pd.DataFrame(
        df.var()).transpose().rename(index={0: 'var'})
    summary_statistics = summary_statistics.append(var_statistics)

    return summary_statistics


user_graph_model = UserGraphModel(mongo_db_connector, graph_db_connector)
user_graph_model.buildModel(add_activity_weight=False)
user_edge_weights = user_graph_model.edges.values()

combined_graph_model = UserGraphModel(mongo_db_connector, graph_db_connector)
combined_graph_model.buildModel(add_activity_weight=True)
edge_weights_combined = combined_graph_model.edges.values()

user_models_edge_weights_df = pd.DataFrame({
    'User model': user_edge_weights,
    'Combined model': edge_weights_combined
})

user_models_statistics = getSummaryStatistics(df=user_models_edge_weights_df)
print(user_models_statistics)

action_graph_model = ActionGraphModel(mongo_db_connector, graph_db_connector)
action_graph_model.buildModel()
action_edge_weights = action_graph_model.edges.values()

action_model_edge_weights_df = pd.DataFrame({
    'Action Model': action_edge_weights
})
action_model_statistics = getSummaryStatistics(df=action_model_edge_weights_df)
print(action_model_statistics)

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
