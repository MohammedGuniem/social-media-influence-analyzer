from classes.statistics.RunningTime import Timer
import pymongo


class MongoDBConnector:
    """ Connection initializer """

    def __init__(self, connection_string, collection_name=None):
        with pymongo.MongoClient(connection_string) as self.client:
            if collection_name:
                self.collection_name = collection_name
            else:
                self.collection_name = self.getMostRecentValidCollection()
            self.timer = Timer()
            self.writing_runtimes = {"created": self.timer.getCurrentTime()}
            self.reading_runtimes = {"created": self.timer.getCurrentTime()}

    """ Collection validator """

    def getMostRecentValidCollection(self):
        collections = [
            set(self.client["Subreddits_DB"].collection_names()),
            set(self.client["New_Submissions_DB"].collection_names()),
            set(self.client["New_Comments_DB"].collection_names()),
            set(self.client["New_Users_DB"].collection_names()),
            set(self.client["Rising_Submissions_DB"].collection_names()),
            set(self.client["Rising_Comments_DB"].collection_names()),
            set(self.client["Rising_Users_DB"].collection_names())
        ]
        valid_collections = collections[0]
        for collection_set in collections:
            valid_collections &= collection_set
        valid_collections = sorted(valid_collections, reverse=True)

        if len(valid_collections) > 0:
            return valid_collections[0]
        return "no valid collection!"

    """ Writing and reading methods """

    def writeToDB(self, database_name, collection_name, data):
        start_time = self.timer.getCurrentTime()
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
        runtime = self.timer.calculate_runtime(start_time)
        self.writing_runtimes[database_name] = runtime

    def get_writing_runtimes(self):
        return self.writing_runtimes

    def readFromDB(self, database_name, query={}, single=False):
        start_time = self.timer.getCurrentTime()
        database = self.client[database_name]
        collection = database[self.collection_name]
        if single:
            docs = collection.find_one(query)
        else:
            docs = list(collection.find(query))
        runtime = self.timer.calculate_runtime(start_time)
        self.reading_runtimes[database_name] = runtime
        return docs

    def get_reading_runtimes(self):
        return self.reading_runtimes

    """ Data Accessors """

    def getRunningTime(self):
        data = self.readFromDB(database_name="admin")
        return data

    def getSubredditInfo(self, display_name):
        data = self.readFromDB(
            database_name="Subreddits_DB",
            query={"display_name": display_name},
            single=True
        )
        return data

    def getSubredditsInfo(self):
        data = self.readFromDB(database_name="Subreddits_DB")
        return data

    def getSubmissionsOnSubreddit(self, subreddit_id, Type):
        data = self.readFromDB(
            database_name=F"{Type}_Submissions_DB",
            query={"subreddit_id": subreddit_id}
        )
        return data

    def getCommentsOnSubmission(self, submission_id, Type):
        data = self.readFromDB(
            database_name=F"{Type}_Comments_DB",
            query={"submission_id": "t3_"+submission_id}
        )
        return data

    def getCommentInfo(self, comment_id, Type):
        data = self.readFromDB(
            database_name=F"{Type}_Comments_DB",
            query={"id": comment_id},
            single=True
        )
        return data

    def getCommentChildren(self, comment_id, Type):
        data = self.readFromDB(
            database_name=F"{Type}_Comments_DB",
            query={"parent_id": F"t1_{comment_id}"}
        )
        return data
