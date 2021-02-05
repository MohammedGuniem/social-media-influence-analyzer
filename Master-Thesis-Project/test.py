from classes.database_connectors.MongoDBConnector import MongoDBConnector
from dotenv import load_dotenv
import os
load_dotenv()

MongoDB_connection_string = os.environ.get('mongo_connnection_string')

mongo_db_connector = MongoDBConnector(MongoDB_connection_string)

collections = [
    set(["2020-03-30", "2020-02-02", "2020-01-30", ""]),
    set(["2020-03-30", "2020-02-02", "2020-01-30"]),
    set(["2020-03-30", "2020-02-02", "2020-01-30"]),
    set(["2020-01-30", "2020-02-02", "2020-03-30"]),
    set(["2020-01-30", "2020-02-02", "2020-03-30"]),
    set(["2020-03-30", "2020-02-02", "2020-03-30"]),
    set(["2020-03-30", "2020-02-02", "2020-03-30"])
]

valid_collections = collections[0]
for collection_set in collections:
    valid_collections &= collection_set
valid_collections = sorted(valid_collections, reverse=True)

print(valid_collections)
