from classes.database_connectors.MongoDBConnector import MongoDBConnector
import pandas as pd
import os

MongoDB_connection_string = os.environ.get('mongo_connnection_string')

# Database connector
MongoDBConnector = MongoDBConnector(MongoDB_connection_string)

# For each subreddit:
# 1) get all new submissions, and make pandas dataframe
# 2) calculate basic statistics for: num_comments, upvotes, upvote_ratio
# 3) calculate time since previous submissions for each submission


target_subreddits = MongoDBConnector.getSubredditsInfo()
submissions = []
for subreddit in target_subreddits:
    print(F"Subreddit: {subreddit['display_name']} {subreddit['id']}")
    submissions += MongoDBConnector.getSubmissionsOnSubreddit(
        subreddit_id=subreddit['id'], Type="New")

submissions_df = pd.DataFrame(submissions)
submissions_df = submissions_df[[
    "id", "author_id", "author_name", "num_comments", "upvotes", "upvote_ratio"]]
print(submissions_df.head(10))
