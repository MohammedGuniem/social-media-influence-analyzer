from classes.database_connectors.MongoDBConnector import MongoDBConnector
import os

connection_string = os.environ.get('mongo_connnection_string')

mongo_db_connector = MongoDBConnector(connection_string)

crawling_analysis = mongo_db_connector.get_crawling_runtimes()

writing_analysis = mongo_db_connector.get_writing_runtimes()

reading_analysis = mongo_db_connector.get_reading_runtimes()
