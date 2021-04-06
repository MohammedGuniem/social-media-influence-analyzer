from classes.database_connectors.MongoDBConnector import MongoDBConnector
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import datetime
import time
import os

load_dotenv()

mongo_db_connector = MongoDBConnector(
    os.environ.get('mongo_connnection_string')
)

network_name = input(
    "Enter the name of the crawled social network: ")  # example: Reddit
submissions_type = input(
    "Enter the type of the crawled submissions, leave empty to select all types: ")  # example: Rising
from_date = input(
    "Enter the start date from which you wish to show crawling log statistics, YYYY-MM-dd: ")  # example: 2021-03-31
from_date = time.mktime(datetime.datetime. strptime(
    from_date, '%Y-%m-%d').timetuple())

runtimes = mongo_db_connector.getCrawlingRuntimes(
    network_name, submissions_type, from_date)

runtimes_df = pd.DataFrame(runtimes)
runtimes_df["date"] = pd.to_datetime(runtimes_df['timestamp'], unit='s')
runtimes_df['date'] = pd.to_datetime(
    runtimes_df['date'], format="%d.%m.%y").astype(dtype="string")

runtimes_df.drop(['timestamp', '_id', 'network_name',
                  'submissions_type'], axis=1, inplace=True)

runtimes_df["per group"] = runtimes_df["groups_crawling_time"] / \
    runtimes_df["groups_count"]
runtimes_df["per submission"] = runtimes_df["submissions_crawling_time"] / \
    runtimes_df["submissions_count"]
runtimes_df["per comment"] = runtimes_df["comments_crawling_time"] / \
    runtimes_df["comments_count"]

runtimes_df.set_index(runtimes_df['date'], inplace=True)
runtimes_df.rename(
    columns={'groups_crawling_time': 'groups', 'submissions_crawling_time': 'submissions', 'comments_crawling_time': 'comments'}, inplace=True)

fig, axes = plt.subplots(1, 2)

runtimes_df[["date", "per group", "per submission", "per comment"]].plot(
    kind="area", stacked=True, ax=axes[0], rot=90, fontsize=6, title="Average Crawling runtimes").set(ylabel='seconds')

runtimes_df[["date", "groups", "submissions", "comments"]].plot(
    kind="area", stacked=True, ax=axes[1], rot=90, fontsize=6, title="Total Crawling runtimes").set(ylabel='seconds')

fig.suptitle('Crawling Runtimes Statistics')

plt.show()
