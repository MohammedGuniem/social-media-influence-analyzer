from pymongo import UpdateOne
from datetime import date
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
        client.close()

    def getSubreddit(self, display_name):
        client = pymongo.MongoClient(self.connection_string)
        database = client["Subreddits_DB"]
        collection = database[str(date.today())]
        client.close()
        return collection.find({"display_name": display_name})

    def getSubmissions(self, subreddit_id):
        client = pymongo.MongoClient(self.connection_string)
        database = client["Submissions_DB"]
        collection = database[str(date.today())]
        client.close()
        return collection.find({"subreddit_ID": subreddit_id})
