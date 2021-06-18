import pymongo
from pymongo import database
from pymongo import results


class MongoDBConnector:
    """ Connection initializer """

    def __init__(self, host, port, user, passowrd):
        with pymongo.MongoClient(host=host, port=port, username=user, password=passowrd, authSource='admin', authMechanism='SCRAM-SHA-256') as self.client:
            pass

    """ Collection validator """

    def getCollectionsOfDatabase(self, database_name):
        collections = set(self.client[database_name].collection_names())
        collections = sorted(collections, reverse=True)

        if len(collections) > 0:
            return collections
        return "no valid collection!"

    def getMostRecentValidCollection(self, database_name):
        collections = set(self.client[database_name].collection_names())
        collections = sorted(collections, reverse=True)

        if len(collections) > 0:
            return collections[0]
        return "no valid collection!"

    """ Writing and reading methods """

    def writeToDB(self, database_name, collection_name, data):
        if not collection_name:
            collection_name = self.getMostRecentValidCollection(database_name)

        if len(data) > 0:
            database = self.client[database_name]
            collection = database[collection_name]
            requests = []
            for entry in data:
                # Insert or update using the upsert option set to True
                if 'id' in entry:
                    requests.append(pymongo.UpdateOne({"id": entry['id']}, {
                                    "$set": entry}, upsert=True))
                else:
                    requests.append(pymongo.InsertOne(entry))

            if len(requests) > 0:
                collection.bulk_write(requests)

    def readFromDB(self, database_name, query={}, single=False, collection_name=None):
        if not collection_name:
            collection_name = self.getMostRecentValidCollection(database_name)

        database = self.client[database_name]
        collection = database[collection_name if collection_name else self.collection_name]
        if single:
            docs = collection.find_one(query)
        else:
            docs = list(collection.find(query))
        return docs

    """ Removal and cleaning methods """

    def remove_collection(self, database_name, collection_name):
        result = self.client[database_name].drop_collection(collection_name)
        return result['ok']

    def remove_crawling_runtime(self, network_name, submissions_type, from_timestamp, to_timestamp):
        result = self.client["admin"]["crawling_runtime_register"].delete_many(
            {"timestamp": {"$gte": from_timestamp, "$lte": to_timestamp}})
        return result.deleted_count

    """ Data Accessors """

    def getGroupInfo(self, network_name, submissions_type, display_name):
        data = self.readFromDB(
            database_name=F"{network_name}_{submissions_type}_Groups_DB",
            query={"display_name": display_name},
            single=True
        )
        return data

    def getGroups(self, network_name, submissions_type):
        data = self.readFromDB(
            database_name=F"{network_name}_{submissions_type}_Groups_DB")
        return data

    def getSubmissionsOnGroup(self, network_name, submissions_type, group_id):
        data = self.readFromDB(
            database_name=F"{network_name}_{submissions_type}_Submissions_DB",
            query={"group_id": group_id}
        )
        return data

    def getCommentsOnSubmission(self, network_name, submissions_type, submission_id):
        data = self.readFromDB(
            database_name=F"{network_name}_{submissions_type}_Comments_DB",
            query={"submission_id": submission_id}
        )
        return data

    def getCommentInfo(self, network_name, submissions_type, comment_id):
        data = self.readFromDB(
            database_name=F"{network_name}_{submissions_type}_Comments_DB",
            query={"id": comment_id},
            single=True
        )
        return data

    def getCommentChildren(self, network_name, submissions_type, comment_id):
        data = self.readFromDB(
            database_name=F"{network_name}_{submissions_type}_Comments_DB",
            query={"parent_id": F"t1_{comment_id}"}
        )
        return data

    def getChildrenCount(self, network_name, submissions_type, comments_array):
        children_array = []
        descendants = []
        for comment in comments_array:
            children = self.getCommentChildren(
                network_name, submissions_type, comment_id=comment['id'])

            children_array += children
            descendants.append(len(children))

        if sum(descendants) == 0:
            return 0
        else:
            score = sum(descendants) + self.getChildrenCount(
                network_name, submissions_type, comments_array=children_array)
        return score

    def getCrawlingRuntimes(self, network_name, submissions_type, from_date):
        query = {
            "network_name": network_name,
            "timestamp": {"$gte": from_date}
        }
        if submissions_type:
            query["submissions_type"] = submissions_type
        database = self.client["admin"]
        collection = database["crawling_runtime_register"]
        runtimes = list(collection.find(query))
        return runtimes
