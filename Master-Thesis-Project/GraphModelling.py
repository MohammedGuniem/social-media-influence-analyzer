from MongoDBConnector import MongoDBConnector


class GraphModel:
    def __init__(self, model_name, mongo_connnection_string):
        self.model_name = model_name
        self.mongo_connnection_string = mongo_connnection_string

    def buildModel(self, subreddit_display_name):
        model = {}
        mongo_db_connector = MongoDBConnector(self.mongo_connnection_string)
        subreddits = mongo_db_connector.getSubreddit(subreddit_display_name)
        submissions = mongo_db_connector.getSubmissions(subreddit_display_name)

        for subreddit in subreddits:
            subreddit_id = subreddit["id"]
            submissions = mongo_db_connector.getSubmissions(subreddit_id)

            for submission in submissions:
                submission_author_id = submission["author_id"]

                for moderator in subreddit["moderators"]:
                    relationship_id = F"{moderator['id']}_{submission_author_id}"
                    relation_node = {
                        "FROM": {
                            "type": "Person",
                            "id": moderator['id'],
                            "data": {"name": moderator['name']}
                        },
                        "RELATIONSHIP": {
                            "type": "DOES_INFLUENCE",
                            "data": {"weight": 1}
                        },
                        "TO": {
                            "type": "Person",
                            "id": submission_author_id,
                            "data": {"name": submission["author_name"]}
                        }
                    }

                    if relationship_id in model:
                        model[relationship_id]["RELATIONSHIP"]["data"]["weight"] += 1
                    else:
                        model[relationship_id] = relation_node

        return model
