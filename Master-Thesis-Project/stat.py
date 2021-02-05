from classes.database_connectors.MongoDBConnector import MongoDBConnector
import pandas as pd
import os

MongoDB_connection_string = os.environ.get('mongo_connnection_string')

# Database connector
MongoDBConnector = MongoDBConnector(MongoDB_connection_string, "New")

target_subreddits = ["Home", "AskReddit", "politics"]

data = []
for subreddit in target_subreddits:
    data.append(MongoDBConnector.getSubredditInfo(display_name=subreddit))

print(len(data))
df = pd.DataFrame(list(data))
print(df.head(n=3))

print(df[["display_name", "id"]])
