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

# Reddit Crawler Object
crawler = RedditCrawler(
    client_id, client_secret, user_agent, username, password)

# Name of social network to be crawled
social_network_name = "Reddit"

# Determing how many groups to crawl
groups_limit = 3

# Setting the submissions type to Rising and Determing how many submissions from each group
submissions_type = "Rising"
submissions_limit = 3

# Crawling groups
groups = crawler.getGroups(groups_limit)

# Writing groups to mongoDB archive
mongo_db_connector.writeToDB(
    database_name=F"{social_network_name}_Groups_DB",
    collection_name=str(date.today()),
    data=groups
)

# Crawling submissions
submissions = crawler.getSubmissions(
    groups, submissions_type, submissions_limit)

# Writing submissions to mongoDB archive
mongo_db_connector.writeToDB(
    database_name=F"{social_network_name}_{submissions_type}_Submissions_DB",
    collection_name=str(date.today()),
    data=submissions
)

# Crawling Comments
comments = crawler.getComments(submissions, submissions_type)

# Writing commments to mongoDB archive
mongo_db_connector.writeToDB(
    database_name=F"{social_network_name}_{submissions_type}_Comments_DB",
    collection_name=str(date.today()),
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
