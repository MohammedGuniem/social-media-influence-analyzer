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
# example: upvotes
score_type = input("Enter target score type, leave empty to view all scores: ")

# Making a neo4j graph connector
neo4j_db_connector = GraphDBConnector(
    uri=os.environ.get('neo4j_connection_string'),
    user=os.environ.get('neo4j_username'),
    password=os.environ.get('neo4j_password')
)

neo4j_graph = neo4j_db_connector.get_graph(
    database=F"usergraph{model_date}", relation_type="Influences")

if score_type:
    score_types = [score_type]
    fig, axes = plt.subplots(2, 1)
    fig.suptitle(F"Influence Scores Distribution using {score_type}")
else:
    score_types = ["interaction", "activity", "upvotes", "interaction_and_activity",
                   "activity_and_upvotes", "interaction_and_upvotes", "total"]
    fig, axes = plt.subplots(2, 7, figsize=(24, 10))
    fig.tight_layout(pad=4.0)
    fig.suptitle("Influence Scores Distribution")

axes = axes.ravel()

links = {}
for score_type in score_types:
    links[F"{score_type}"] = []
    for link in neo4j_graph["links"]:
        links[F"{score_type}"].append(link['props'][F"{score_type}"])

links_df = pd.DataFrame(links)

for score_type in score_types:
    links_df[F"{score_type}"].plot(
        kind="box",
        ax=axes[score_types.index(score_type)],
        title=F"{score_type} score"
    )

    links_df[F"{score_type}"].plot(
        kind="hist",
        bins=links_df[F"{score_type}"].nunique(),
        ax=axes[score_types.index(score_type)+len(score_types)],
        title=F"{score_type} score",
        xticks=links_df[F"{score_type}"],
        rot=90
    )

plt.show()
