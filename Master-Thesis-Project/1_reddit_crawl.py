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

# Database connector
mongo_db_connector = MongoDBConnector(MongoDB_connection_string)

# Reddit crawler
crawler = RedditCrawler(
    client_id, client_secret, user_agent, username, password)

# Name of social network to be crawled
social_network_name = "Reddit"

# Setting the submissions type to Rising
submissions_type = "Rising"

# Crawling groups
groups = crawler.getGroups(top_n_subreddits=5)

# Crawling submissions
submissions = crawler.getSubmissions(
    subreddits=groups, submission_limit=5, submissions_type=submissions_type)

# Crawling Comments
comments = crawler.getComments(submissions, submissions_type)

collection_name = str(date.today())

# Writing groups/subreddits to mongoDB archive
mongo_db_connector.writeToDB(
    database_name=F"{social_network_name}_Groups_DB",
    collection_name=collection_name,
    data=groups
)

# Writing submissions to mongoDB archive
mongo_db_connector.writeToDB(
    database_name=F"{social_network_name}_{submissions_type}_Submissions_DB",
    collection_name=collection_name,
    data=submissions
)

# Writing comments to mongoDB archive
mongo_db_connector.writeToDB(
    database_name=F"{social_network_name}_{submissions_type}_Comments_DB",
    collection_name=collection_name,
    data=comments
)

# Fetching the registered runtimes from this crawling run
runtime_register = crawler.runtime_register.getRunningTime()

# logging the runtime register into admin DB in mongoDB
mongo_db_connector.writeToDB(
    database_name="admin",
    collection_name="crawling_runtime_register",
    data=[runtime_register]
)
