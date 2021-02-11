class UserGraphModel:
    def __init__(self, mongo_db_connector, graph_db_connector):
        self.mongo_db_connector = mongo_db_connector
        self.graph_db_connector = graph_db_connector
        self.nodes = {}
        self.edges = {}

    def addNode(self, activity_object, Type):
        props = {}

        if Type == "Redditor":
            node_id = activity_object["author_id"]
            props["name"] = activity_object["author_name"]

        elif Type == "Subreddit":
            node_id = activity_object['id']
            props["name"] = activity_object['display_name']
            props["moderators_names"] = []
            props["moderators_ids"] = []
            for moderator in activity_object["moderators"]:
                props["moderators_ids"].append(moderator['id'])
                props["moderators_names"].append(moderator['name'])

        if not node_id in self.nodes:
            self.graph_db_connector.addNode(
                node_id, Type, props)
            self.nodes[node_id] = True

    def addEdge(self, from_ID, from_Type, to_ID, to_Type, score):
        edge_id = F"{from_ID}_{to_ID}"
        if edge_id in self.edges:
            self.edges[edge_id] += score
        else:
            self.edges[edge_id] = score

        self.graph_db_connector.addEdge(
            relation_Type="Influences",
            relation_props={"weight": self.edges[edge_id]},
            from_ID=from_ID,
            from_Type=from_Type,
            to_ID=to_ID,
            to_Type=to_Type
        )

    def buildModel(self, subreddit_display_name=None, submission_type=None):
        # Get subreddit information.
        subreddit = self.mongo_db_connector.getSubredditInfo(
            subreddit_display_name)

        # Draw subreddit, containing its moderators
        self.addNode(activity_object=subreddit, Type="Subreddit")

        # Get all submissions on this subreddit.
        subreddit_id = subreddit['id']
        submissions = self.mongo_db_connector.getSubmissionsOnSubreddit(
            subreddit_id, submission_type)

        comments = []
        for submission in submissions:
            submission_author_id = submission["author_id"]

            # Draw submission authors
            self.addNode(activity_object=submission, Type="Redditor")

            # Draw influence relation between subreddit and submission author
            self.addEdge(
                from_ID=subreddit_id,
                from_Type="Subreddit",
                to_ID=submission_author_id,
                to_Type="Redditor",
                score=1
            )

            # Get all comments on submissions on this subreddit
            comments += self.mongo_db_connector.getCommentsOnSubmission(
                submission['id'],
                submission_type
            )

        for comment in comments:
            comment_author_id = comment['author_id']

            # Draw commenters
            self.addNode(activity_object=comment, Type="Redditor")

            parent_id_prefix = comment['parent_id'][0:2]
            parent_id = comment['parent_id'][3:]

            # Comment is top-level
            if parent_id_prefix == "t3":
                # Draw influence relation between submission author and top-level commenters
                self.addEdge(
                    from_ID=submission_author_id,
                    from_Type="Redditor",
                    to_ID=comment_author_id,
                    to_Type="Redditor",
                    score=1
                )

            # Comment is a thread comment
            elif parent_id_prefix == "t1":
                parent_comment = self.mongo_db_connector.getCommentInfo(
                    comment_id=parent_id,
                    Type=submission_type
                )

                # Draw influence relation between parent commenters and child commenters
                self.addEdge(
                    from_ID=parent_comment["author_id"],
                    from_Type="Redditor",
                    to_ID=comment_author_id,
                    to_Type="Redditor",
                    score=1
                )
