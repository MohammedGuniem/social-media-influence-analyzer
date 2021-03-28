from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.crawling.TestCrawlClass import TestCrawler
from dotenv import load_dotenv
from datetime import date
import os

load_dotenv()

MongoDB_connection_string = os.environ.get('mongo_connnection_string')

# Database connector
mongo_db_connector = MongoDBConnector(MongoDB_connection_string)

# Dummy test case crawler
crawler = TestCrawler()

# Crawling dummy groups
groups = crawler.getGroups()

# Name of social network to be crawled
social_network_name = "Test"

# Writing dummy groups to mongoDB archive
mongo_db_connector.writeToDB(
    database_name=F"{social_network_name}_Groups_DB",
    collection_name=str(date.today()),
    data=groups
)

# Crawling dummy submissions
submissions = crawler.getSubmissions()

# Assuming the submissions type is new
submissions_type = "New"

# Writing dummy submissions to mongoDB archive
mongo_db_connector.writeToDB(
    database_name=F"{social_network_name}_{submissions_type}_Submissions_DB",
    collection_name=str(date.today()),
    data=submissions
)

# Crawling dummy Comments
comments = crawler.getComments()

# Writing dummy submissions to mongoDB archive
mongo_db_connector.writeToDB(
    database_name=F"{social_network_name}_{submissions_type}_Comments_DB",
    collection_name=str(date.today()),
    data=comments
)
