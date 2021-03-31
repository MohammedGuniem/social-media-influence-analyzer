from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.crawling.TestCrawlClass import TestCrawler
from dotenv import load_dotenv
from datetime import date
import os

load_dotenv()

MongoDB_connection_string = os.environ.get('mongo_connnection_string')

# Database connector
mongo_db_connector = MongoDBConnector(MongoDB_connection_string)

# Reddit crawler
crawler = TestCrawler()

# Name of social network to be crawled
social_network_name = "Test"

# Assuming we are crawling the newest submissions
submissions_type = "New"

# Crawling groups/subreddits
groups = crawler.getGroups()

# Crawling submissions
submissions = crawler.getSubmissions()

# Crawling Comments
comments = crawler.getComments()

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
