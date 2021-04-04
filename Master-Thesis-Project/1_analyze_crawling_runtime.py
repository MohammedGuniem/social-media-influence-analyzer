from classes.database_connectors.MongoDBConnector import MongoDBConnector
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
    "Enter the type of the crawled submissions, leave empty to select all types: ")  # example: Rising

runtimes = mongo_db_connector.getCrawlingRuntimes(
    network_name, submissions_type)
runtimes_df = pd.DataFrame(runtimes)
runtimes_df["date"] = pd.to_datetime(runtimes_df['timestamp'], unit='s')
runtimes_df['date'] = pd.to_datetime(
    runtimes_df['date'], format="%d.%m.%y").astype(dtype="string")

runtimes_df.drop(['timestamp', '_id', 'network_name',
                  'submissions_type'], axis=1, inplace=True)

runtimes_df["per_group"] = runtimes_df["groups_crawling_time"] / \
    runtimes_df["groups_count"]
runtimes_df["per_submission"] = runtimes_df["submissions_crawling_time"] / \
    runtimes_df["submissions_count"]
runtimes_df["per_comment"] = runtimes_df["comments_crawling_time"] / \
    runtimes_df["comments_count"]

runtimes_df.set_index(runtimes_df['date'], inplace=True)

runtimes_df[["date", "per_group", "per_submission", "per_comment"]].plot(
    kind="area", stacked=True)

plt.xticks(fontsize=6, rotation=90)
plt.show()
