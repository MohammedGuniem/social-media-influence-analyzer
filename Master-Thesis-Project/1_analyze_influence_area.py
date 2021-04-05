from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import os

load_dotenv()

mongo_db_connector = MongoDBConnector(
    os.environ.get('mongo_connnection_string')
)

network_name = input(
    "Enter the name of the crawled social network: ")  # example: Reddit
submissions_type = input(
    "Enter the type of the crawled submissions: ")  # example: Rising
model_date = input(
    "Enter the date the neo4j user model was built in, YYYY-MM-dd: ").replace("-", "")  # example: 2021-04-02

groups = mongo_db_connector.getGroups(network_name)

submissions = []
for group in groups:
    group_submissions = mongo_db_connector.getSubmissionsOnGroup(
        network_name, submissions_type, group['id'])
    submissions += group_submissions

groups_df = pd.DataFrame(groups).rename(
    columns={'id': 'group_id'}).drop(['_id'], axis=1)

submissions_df = pd.DataFrame(submissions).drop(['_id'], axis=1)

submissions_df = pd.merge(submissions_df, groups_df,
                          how='outer', on=['group_id'])

fig, axes = plt.subplots(1, 2)

submissions_df.groupby("display_name")["display_name"].count().plot(
    kind="pie", ax=axes[0], title="Crawled Groups").axis("off")

# Making a neo4j graph connector
neo4j_db_connector = GraphDBConnector(
    uri=os.environ.get('neo4j_connection_string'),
    user=os.environ.get('neo4j_username'),
    password=os.environ.get('neo4j_password')
)

neo4j_graph = neo4j_db_connector.get_graph(
    database=F"usergraph{model_date}", relation_type="Influences")

predicted_influence = []
for link in neo4j_graph["links"]:
    predicted_influence += link["props"]["influence_areas"]

predicted_influence_df = pd.DataFrame(
    predicted_influence, columns=["predicted_influence"])

predicted_influence_df.groupby("predicted_influence")[
    "predicted_influence"].count().plot(kind="pie", ax=axes[1], title="Predicted Influence Areas").axis("off")

fig.suptitle('Horizontally stacked subplots')

plt.show()
