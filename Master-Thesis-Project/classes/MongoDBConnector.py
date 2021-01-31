from pymongo import UpdateOne
from datetime import date
import pymongo


class MongoDBConnector:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.database = "2021-01-30"

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
        collection = database[self.database]
        client.close()
        return list(collection.find({"display_name": display_name}))

    def getSubmissions(self, subreddit_id):
        client = pymongo.MongoClient(self.connection_string)
        database = client["Submissions_DB"]
        collection = database[self.database]
        client.close()
        return list(collection.find({"subreddit_ID": subreddit_id}))

    def getCommentsBySubmissionID(self, submission_id):
        client = pymongo.MongoClient(self.connection_string)
        database = client["Comments_DB"]
        collection = database[self.database]
        client.close()
        return list(collection.find({"submission_ID": F"t3_{submission_id}"}))

    def getComments(self, subreddit_id):
        client = pymongo.MongoClient(self.connection_string)
        database = client["Comments_DB"]
        collection = database[self.database]
        client.close()
        return list(collection.find({"subreddit_id": F"t5_{subreddit_id}"}))

    def getSubmissionByID(self, submission_id):
        client = pymongo.MongoClient(self.connection_string)
        database = client["Submissions_DB"]
        collection = database[self.database]
        client.close()
        return list(collection.find({"id": submission_id}))

    def getCommentByID(self, comment_id):
        client = pymongo.MongoClient(self.connection_string)
        database = client["Comments_DB"]
        collection = database[self.database]
        client.close()
        return list(collection.find({"id": comment_id}))

    def getComments(self, submission_id):
        client = pymongo.MongoClient(self.connection_string)
        database = client["Comments_DB"]
        collection = database[self.database]
        client.close()
        return list(collection.find({"submission_ID": F"t3_{submission_id}"}))
