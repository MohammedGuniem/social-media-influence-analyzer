from classes.database_connectors.MongoDBConnector import MongoDBConnector
from dotenv import load_dotenv
import os
load_dotenv()

MongoDB_connection_string = os.environ.get('mongo_connnection_string')

mongo_db_connector = MongoDBConnector(MongoDB_connection_string)
