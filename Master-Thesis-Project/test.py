from classes.database_connectors.MongoDBConnector import MongoDBConnector
from dotenv import load_dotenv
import os
load_dotenv()

MongoDB_connection_string = os.environ.get('mongo_connnection_string')

mongo_db_connector = MongoDBConnector(MongoDB_connection_string)

a = []

a += ["a", "b"]
a += ["c"]

print(a)


def f():
    return ["a"], ["b"]


a, b = ["1"], ["2"]
r = f()
print(r[0])
a, b = r[0], r[1]
print(a)
