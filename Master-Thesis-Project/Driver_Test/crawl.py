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

# Name of social network to be crawled
social_network_name = "Test"

# Setting the submissions type to Rising
submissions_type = "New"

# Crawling dummy test groups
groups = crawler.getGroups()

# Writing dummy test groups to mongoDB archive
mongo_db_connector.writeToDB(
    database_name=F"{social_network_name}_Groups_DB",
    collection_name=str(date.today()),
    data=groups
)

# Crawling dummy test submissions
submissions = crawler.getSubmissions()

# Assuming the dummy test submissions type is new
submissions_type = "New"

# Writing dummy test submissions to mongoDB archive
mongo_db_connector.writeToDB(
    database_name=F"{social_network_name}_{submissions_type}_Submissions_DB",
    collection_name=str(date.today()),
    data=submissions
)

# Crawling dummy test Comments
comments = crawler.getComments()

# Writing dummy test submissions to mongoDB archive
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
