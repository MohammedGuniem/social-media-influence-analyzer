from pymongo import UpdateOne
from datetime import date
import pymongo


class MongoDBConnector:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.valid_collections, self.non_valid_collections = self.validateCollections()
        self.database = self.valid_collections[0]

    def validateCollections(self):
        client = pymongo.MongoClient(self.connection_string)
        collections = [
            set(client["Subreddits_DB"].collection_names()),
            set(client["Submissions_DB"].collection_names()),
            set(client["Comments_DB"].collection_names()),
            set(client["Users_DB"].collection_names()),
        ]
        valid_collections = sorted(
            collections[0] & collections[1] & collections[2] & collections[3], reverse=True)
        non_valid_collections = sorted(
            collections[0] ^ collections[1] ^ collections[2] ^ collections[3], reverse=True)

        client.close()
        return valid_collections, non_valid_collections

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

    def getSubredditInfo(self, display_name):
        client = pymongo.MongoClient(self.connection_string)
        database = client["Subreddits_DB"]
        collection = database[self.database]
        client.close()
        return list(collection.find({"display_name": display_name}))[0]

    def getSubmissionsOnSubreddit(self, subreddit_id):
        client = pymongo.MongoClient(self.connection_string)
        database = client["Submissions_DB"]
        collection = database[self.database]
        client.close()
        return list(collection.find({"subreddit_ID": subreddit_id}))

    def getCommentsOnSubmission(self, submission_id):
        client = pymongo.MongoClient(self.connection_string)
        database = client["Comments_DB"]
        collection = database[self.database]
        client.close()
        return list(collection.find({"submission_ID": F"t3_{submission_id}"}))

    def getCommentInfo(self, comment_id):
        client = pymongo.MongoClient(self.connection_string)
        database = client["Comments_DB"]
        collection = database[self.database]
        client.close()
        return list(collection.find({"id": comment_id}))[0]
