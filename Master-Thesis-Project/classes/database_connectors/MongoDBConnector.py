from pymongo import UpdateOne
from datetime import date
import pymongo


class MongoDBConnector:
    def __init__(self, connection_string, Type=None):
        self.connection_string = connection_string
        self.Type = Type
        if self.Type:
            self.valid_collections, self.non_valid_collections = self.validateCollections(
                self.Type)
            self.collection = self.valid_collections[0]
            print(self.collection)

    def validateCollections(self, Type):
        client = pymongo.MongoClient(self.connection_string)
        collections = [
            set(client["Subreddits_DB"].collection_names()),
            set(client[F"{Type}_Submissions_DB"].collection_names()),
            set(client[F"{Type}_Comments_DB"].collection_names()),
            set(client[F"{Type}_Users_DB"].collection_names()),
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
                if 'id' in entry:
                    requests.append(UpdateOne({"id": entry['id']}, {
                                    "$set": entry}, upsert=True))
                else:
                    print(entry)
            collection.bulk_write(requests)
        client.close()

    def getSubredditInfo(self, display_name):
        client = pymongo.MongoClient(self.connection_string)
        database = client["Subreddits_DB"]
        collection = database[self.collection]
        client.close()
        data = list(collection.find({"display_name": display_name}))
        if len(data) > 0:
            return data[0]
        else:
            return []

    def getSubmissionsOnSubreddit(self, subreddit_id):
        client = pymongo.MongoClient(self.connection_string)
        database = client[F"{self.Type}_Submissions_DB"]
        collection = database[self.collection]
        client.close()
        return list(collection.find({"subreddit_ID": subreddit_id}))

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
