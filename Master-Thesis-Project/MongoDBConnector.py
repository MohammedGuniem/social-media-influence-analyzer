from pymongo import UpdateOne
import pymongo


class MongoDBConnector:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def writeToMongoDB(self, database_name, collection_name, data):
        client = pymongo.MongoClient(self.connection_string)
        database = client[database_name]
        collection = database[collection_name]
        if len(data) > 0:
            requests = []
            for entry in data:
                # Insert or update using the upsert option set to True
                requests.append(UpdateOne({"id": entry['id']}, {
                                "$set": entry}, upsert=True))
            collection.bulk_write(requests)
