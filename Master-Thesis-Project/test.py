from classes.database_connectors.MongoDBConnector import MongoDBConnector
from dotenv import load_dotenv
import os
load_dotenv()

MongoDB_connection_string = os.environ.get('mongo_connnection_string')

mongo_db_connector = MongoDBConnector(MongoDB_connection_string, "New")

a = {"a": 0, "b": 1}
b = {"c": 3}

d = a

d |= b

print(d)

a = [0, 1, 2]
b = [3]
print(a + b)
