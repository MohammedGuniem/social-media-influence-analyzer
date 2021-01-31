from classes.MongoDBConnector import MongoDBConnector


class GraphModel:
    def __init__(self, model_name, mongo_connnection_string):
        self.model_name = model_name
        self.mongo_connnection_string = mongo_connnection_string

    def makeSubredditNode(self, subreddit):
        node = {
            "type": "Subreddit",
            "id": subreddit['id'],
            "data": {"name": subreddit['display_name']}
        }
        return node

    def makeSubmissionNode(self, submission):
        nodes = {
            "type": "Submission",
            "id": submission['id'],
            "data": {"name": submission['author_name']}
        }
        return nodes

    def makeCommentNode(self, comment, Type):
        node = {
            "type": Type,
            "id": comment['id'],
            "data": {"name": comment['author_name']}
        }
        return node

    def makeRelation(self, Type, weight):
        relation = {
            "type": Type,
            "data": {"weight": weight}
        }
        return relation

    def makeRelationship(self, from_node, to_node, Type, weight):
        relationship = {
            "FROM": from_node,
            "RELATIONSHIP": self.makeRelation(Type=Type, weight=weight),
            "TO": to_node
        }
        return relationship

    def buildUserModel(self, subreddit_display_name, moderator_weight=1, submission_author_weight=1, parent_comment_author_weight=1):
        model = {}
        mongo_db_connector = MongoDBConnector(self.mongo_connnection_string)
        subreddits = mongo_db_connector.getSubreddit(subreddit_display_name)

        for subreddit in subreddits:
            subreddit_id = subreddit["id"]
            submissions = mongo_db_connector.getSubmissions(subreddit_id)

            for moderator in subreddit["moderators"]:
                moderator_id = moderator['id']
                for submission in submissions:
                    relation_id = F"{moderator_id}_{submission['author_id']}"
                    relation_node = self.makeRelationship(
                        moderator, submission, Type="Influences", moderator_weight)
                    if relation_id in model:
                        model[relation_id]['RELATIONSHIP']['data']['weight'] += relation_node['RELATIONSHIP']['data']['weight']
                    else:
                        model[relation_id] = relation_node

            comments = mongo_db_connector.getComments(subreddit_id)
            print(F"Number of comments: {len(comments)}")

            for comment in comments:
                # If root comment
                prefix = comment["parent_ID"][0:3]
                if prefix == "t3_":
                    # submission author gets 1 points
                    submission_id = comment["parent_ID"][3:]
                    submission = mongo_db_connector.getSubmissionByID(submission_id)[
                        0]
                    user = {
                        'id': submission['author_id'],
                        'name': submission['author_name']
                    }
                    relation_id = F"{submission['author_id']}_{comment['author_id']}"
                    relation_node = self.makeRelationship(
                        user, submission, submission_author_weight)

                # If thread comment
                elif prefix == "t1_":
                    # comment author gets 1 points
                    parent_comment_id = comment["parent_ID"][3:]
                    parent_comment = mongo_db_connector.getCommentByID(parent_comment_id)[
                        0]
                    user = {
                        'id': parent_comment['author_id'],
                        'name': parent_comment['author_name']
                    }
                    relation_id = F"{parent_comment['author_id']}_{comment['author_id']}"
                    relation_node = self.makeRelationship(
                        user, comment, parent_comment_author_weight)

                if relation_id in model:
                    model[relation_id]['RELATIONSHIP']['data']['weight'] += relation_node['RELATIONSHIP']['data']['weight']
                else:
                    model[relation_id] = relation_node

        return model

    def buildSubredditFlowModel(self, subreddit_display_name):
        model = {}
        mongo_db_connector = MongoDBConnector(self.mongo_connnection_string)
        subreddits = mongo_db_connector.getSubreddit(subreddit_display_name)

        for subreddit in subreddits:
            subreddit_node = self.makeSubredditNode(subreddit)
            submissions = mongo_db_connector.getSubmissions(subreddit['id'])
            for submission in submissions:
                submission_node = self.makeSubmissionNode(submission)
                submission_weight = round(submission["upvotes"] *
                                          submission["upvote_ratio"], 2)
                submission_id = submission_node['id']
                relation_id = F"{subreddit_node['id']}_{submission_id}"
                relationship = self.makeRelationship(
                    from_node=subreddit_node, to_node=submission_node, Type="Includes", weight=submission_weight)
                model[relation_id] = relationship

                comments = mongo_db_connector.getComments(
                    submission_id=submission_id)

                for comment in comments:
                    prefix = comment["parent_ID"][0:3]
                    parent_id = comment["parent_ID"][3:]

                    if prefix == "t3_":
                        root_comment_node = self.makeCommentNode(
                            comment=comment, Type="Comment")
                        relation_id = F"{submission_id}_{root_comment_node['id']}"
                        relationship = self.makeRelationship(
                            from_node=submission_node, to_node=root_comment_node, Type="Has", weight=comment['upvotes'])
                        model[relation_id] = relationship

                    elif prefix == "t1_":
                        thread_comment_node = self.makeCommentNode(
                            comment=comment, Type="ThreadComment")
                        parent_comment = mongo_db_connector.getCommentByID(
                            comment_id=parent_id)[0]
                        if parent_comment['submission_ID'] == parent_comment['parent_ID']:
                            parent_comment_type = "Comment"
                        else:
                            parent_comment_type = "ThreadComment"
                        parent_comment_node = self.makeCommentNode(
                            comment=parent_comment, Type=parent_comment_type)
                        relation_id = F"{parent_comment_node['id']}_{thread_comment_node['id']}"
                        relationship = self.makeRelationship(
                            from_node=parent_comment_node, to_node=thread_comment_node, Type="Has", weight=comment['upvotes'])
                        model[relation_id] = relationship
        return model
