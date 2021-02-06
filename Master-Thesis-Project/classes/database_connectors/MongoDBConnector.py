from pymongo import UpdateOne
from datetime import date
import pymongo


class MongoDBConnector:
    def __init__(self, connection_string, collection_name=None):
        self.connection_string = connection_string
        if collection_name:
            self.collection = collection_name
        else:
            self.collection = self.getMostRecentValidCollection()

    def getMostRecentValidCollection(self):
        client = pymongo.MongoClient(self.connection_string)
        collections = [
            set(client["Subreddits_DB"].collection_names()),
            set(client["New_Submissions_DB"].collection_names()),
            set(client["New_Comments_DB"].collection_names()),
            set(client["New_Users_DB"].collection_names()),
            set(client["Rising_Submissions_DB"].collection_names()),
            set(client["Rising_Comments_DB"].collection_names()),
            set(client["Rising_Users_DB"].collection_names())
        ]
        valid_collections = collections[0]
        for collection_set in collections:
            valid_collections &= collection_set
        valid_collections = sorted(valid_collections, reverse=True)

        client.close()
        if len(valid_collections) > 0:
            return valid_collections[0]
        else:
            return "no valid collection!"

    def writeToMongoDB(self, database_name, collection_name, data):
        client = pymongo.MongoClient(self.connection_string)
        database = client[database_name]
        collection = database[collection_name]
        if len(data) > 0:
            requests = []
            for entry in data:
                # Insert or update using the upsert option set to True
                if 'id' in entry:
                    requests.append(UpdateOne({"id": entry['id']}, {
                                    "$set": entry}, upsert=True))
                else:
                    print(entry)
            collection.bulk_write(requests)
        client.close()

    def getSubredditsInfo(self):
        client = pymongo.MongoClient(self.connection_string)
        database = client["Subreddits_DB"]
        collection = database[self.collection]
        client.close()
        data = list(collection.find())
        return data

    def getSubmissionsOnSubreddit(self, subreddit_id, Type):
        client = pymongo.MongoClient(self.connection_string)
        database = client[F"{Type}_Submissions_DB"]
        collection = database[self.collection]
        client.close()
        return list(collection.find({"subreddit_id": subreddit_id}))

    def getRunningTime(self):
        client = pymongo.MongoClient(self.connection_string)
        database = client["admin"]
        collection = database[self.collection]
        client.close()
        return list(collection.find())

#

    def getCommentsOnSubmission(self, submission_id):
        client = pymongo.MongoClient(self.connection_string)
        database = client[F"{self.Type}_Comments_DB"]
        collection = database[self.collection]
        client.close()
        return list(collection.find({"submission_ID": F"t3_{submission_id}"}))

    def getCommentInfo(self, comment_id):
        client = pymongo.MongoClient(self.connection_string)
        database = client[F"{self.Type}_Comments_DB"]
        collection = database[self.collection]
        client.close()
        return list(collection.find({"id": comment_id}))[0]
