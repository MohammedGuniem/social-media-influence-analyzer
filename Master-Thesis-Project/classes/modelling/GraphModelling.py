from classes.MongoDBConnector import MongoDBConnector


class GraphModel:
    def __init__(self, mongo_connnection_string):
        self.mongo_connnection_string = mongo_connnection_string

    """ Common Methods for all models """

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

    def setRelationship(self, model, relation_id, relationship):
        if relation_id in model:
            model[relation_id]['RELATIONSHIP']['data']['weight'] += relationship['RELATIONSHIP']['data']['weight']
        else:
            model[relation_id] = relationship
        return model

    def makeSubredditNode(self, subreddit):
        node = {
            "type": "Subreddit",
            "id": subreddit['id'],
            "data": {
                "name": subreddit['display_name'],
                "moderators_ids": [],
                "moderators_names": []
            }
        }
        for moderator in subreddit['moderators']:
            node['data']['moderators_ids'].append(moderator['id'])
            node['data']['moderators_names'].append(moderator['name'])
        return node

    """ Methods used in (Subreddit Object Flow Model) """

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

    # Building Subreddit Object Flow Model
    def buildSubredditObjectFlowModel(self, subreddit_display_name):
        model = {}
        mongo_db_connector = MongoDBConnector(self.mongo_connnection_string)
        subreddit = mongo_db_connector.getSubredditInfo(
            subreddit_display_name)

        subreddit_node = self.makeSubredditNode(subreddit)
        submissions = mongo_db_connector.getSubmissionsOnSubreddit(
            subreddit_id=subreddit['id'])

        for submission in submissions:
            submission_node = self.makeSubmissionNode(submission)
            submission_weight = round(
                submission["upvotes"] * submission["upvote_ratio"], 2)
            submission_id = submission_node['id']
            relation_id = F"{subreddit_node['id']}_{submission_id}"
            relationship = self.makeRelationship(
                from_node=subreddit_node, to_node=submission_node, Type="Includes", weight=submission_weight)
            model[relation_id] = relationship

            comments = mongo_db_connector.getCommentsOnSubmission(
                submission_id=submission_id)

            for comment in comments:
                prefix = comment["parent_id"][0:3]
                parent_id = comment["parent_id"][3:]

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
                    parent_comment = mongo_db_connector.getCommentInfo(
                        comment_id=parent_id)
                    if parent_comment['submission_id'] == parent_comment['parent_id']:
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

    """ Methods used in (Subreddit User Flow Model) """

    def makeRedditorNode(self, submission_or_comment):
        node = {
            "type": "Redditor",
            "id": submission_or_comment['author_id'],
            "data": {"name": submission_or_comment['author_name']}
        }
        return node

    # Building Subreddit User Flow Model
    def buildSubredditUserModel(self, subreddit_display_name):
        model = {}
        mongo_db_connector = MongoDBConnector(self.mongo_connnection_string)
        subreddit = mongo_db_connector.getSubredditInfo(subreddit_display_name)

        submissions = mongo_db_connector.getSubmissionsOnSubreddit(
            subreddit_id=subreddit['id'])

        moderators_node = self.makeSubredditNode(subreddit)

        for submission in submissions:
            submission_author_node = self.makeRedditorNode(
                submission_or_comment=submission)
            submission_author_weight = round(
                submission["upvotes"] * submission["upvote_ratio"], 2)

            relation_id = F"{subreddit['id']}_{submission['author_id']}"
            relationship = self.makeRelationship(
                from_node=moderators_node, to_node=submission_author_node, Type="Influences", weight=submission_author_weight)

            model = self.setRelationship(
                model=model, relation_id=relation_id, relationship=relationship)

            submission_id = submission['id']
            comments = mongo_db_connector.getCommentsOnSubmission(
                submission_id=submission_id)

            for comment in comments:
                prefix = comment["parent_id"][0:3]
                parent_id = comment["parent_id"][3:]

                relation_id = F"{submission['author_id']}_{comment['author_id']}"
                comment_upvotes = comment['upvotes']

                if prefix == "t3_":
                    comment_author_node = self.makeRedditorNode(
                        submission_or_comment=comment)
                    relationship = self.makeRelationship(
                        from_node=submission_author_node, to_node=comment_author_node, Type="Influences", weight=comment_upvotes)

                elif prefix == "t1_":
                    parent_comment = mongo_db_connector.getCommentInfo(
                        comment_id=parent_id)

                    parent_comment_author_node = self.makeRedditorNode(
                        submission_or_comment=parent_comment)

                    thread_comment_author_node = self.makeRedditorNode(
                        submission_or_comment=comment)

                    relation_id = F"{parent_comment['author_id']}_{comment['author_id']}"

                    relationship = self.makeRelationship(
                        from_node=parent_comment_author_node, to_node=thread_comment_author_node, Type="Influences", weight=comment_upvotes)

                model = self.setRelationship(
                    model=model, relation_id=relation_id, relationship=relationship)

        return model
