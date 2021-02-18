from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.crawling.RedditCrawlClass import RedditCrawler
from dotenv import load_dotenv
from datetime import date
import os

load_dotenv()

client_id = os.environ.get('reddit_client_id')
client_secret = os.environ.get('reddit_client_secret')
user_agent = os.environ.get('reddit_user_agent')
username = os.environ.get('reddit_username')
password = os.environ.get('reddit_password')
MongoDB_connection_string = os.environ.get('mongo_connnection_string')

crawler = RedditCrawler(
    client_id, client_secret, user_agent, username, password)

# A limit for the number of subreddits to crawl
subreddit_limit = 2

# A limit for the number of submissions to crawl
submission_limit = 2

# submissions_type of submissions to crawl
submissions_types = []
submissions_types.append("New")
submissions_types.append("Rising")
# submissions_types.append("Hot")
# submissions_types.append("Top")

# Database connector
MongoDBConnector = MongoDBConnector(MongoDB_connection_string)

# Target Subreddits (subreddit_limit? Most pupolar)
subreddits = crawler.crawlPopularSubreddits(
    subreddit_limit=subreddit_limit
)
subreddits_num = len(subreddits)
print("----------------------------------------------")
print("#subreddits: ", subreddits_num)
print("----------------------------------------------")

MongoDBConnector.writeToDB(
    database_name="Subreddits_DB",
    collection_name=str(date.today()),
    data=subreddits
)

users = []

for submissions_type in submissions_types:
    print("----------------------------------------------")
    print(F"Crawling {submissions_type} Submissions...")
    print("----------------------------------------------")

    submissions, authors = crawler.crawlSubmissions(
        subreddits, submissions_type, submission_limit)
    users += authors

    MongoDBConnector.writeToDB(
        database_name=F"{submissions_type}_Submissions_DB",
        collection_name=str(date.today()),
        data=submissions
    )

    comments, commenters = crawler.crawlComments(
        submissions=submissions,
        submissions_type=submissions_type
    )
    users += commenters

    MongoDBConnector.writeToDB(
        database_name=F"{submissions_type}_Comments_DB",
        collection_name=str(date.today()),
        data=comments
    )

    MongoDBConnector.writeToDB(
        database_name=F"{submissions_type}_Users_DB",
        collection_name=str(date.today()),
        data=users
    )

running_times = crawler.get_running_times()

MongoDBConnector.writeToDB(
    database_name="admin",
    collection_name=str(date.today()),
    data=[running_times]
)
