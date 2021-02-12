class ActionGraphModel:
    def __init__(self, mongo_db_connector, graph_db_connector):
        self.mongo_db_connector = mongo_db_connector
        self.graph_db_connector = graph_db_connector
        self.nodes = {}
        self.edges = {}

    def addNode(self, activity_object, Type):
        props = {}

        if Type == "Subreddit":
            node_id = activity_object['id']
            props["name"] = activity_object['display_name']
            props["moderators_names"] = []
            props["moderators_ids"] = []
            for moderator in activity_object["moderators"]:
                props["moderators_ids"].append(moderator['id'])
                props["moderators_names"].append(moderator['name'])

        elif Type in ["Submission", "Top_comment", "Subcomment"]:
            node_id = activity_object["id"]
            props["name"] = activity_object["author_name"]
            props["author_id"] = activity_object["author_id"]

        if not node_id in self.nodes:
            self.graph_db_connector.addNode(
                node_id, Type, props)
            self.nodes[node_id] = Type

    def addEdge(self, from_ID, to_ID, score):
        edge_id = F"{from_ID}_{to_ID}"
        if edge_id in self.edges:
            self.edges[edge_id] += score
        else:
            self.edges[edge_id] = score

        self.graph_db_connector.addEdge(
            relation_Type="Influences",
            relation_props={"weight": self.edges[edge_id]},
            from_ID=from_ID,
            from_Type=self.nodes[from_ID],
            to_ID=to_ID,
            to_Type=self.nodes[to_ID],
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
            submission_id = submission["id"]

            # Draw submission authors
            self.addNode(activity_object=submission, Type="Submission")

            # Draw influence relation between subreddit and submission
            self.addEdge(
                from_ID=subreddit_id,
                to_ID=submission_id,
                score=round(submission["upvote_ratio"]*submission["upvotes"])
            )

            # Get all comments on submissions on this subreddit
            comments += self.mongo_db_connector.getCommentsOnSubmission(
                submission_id,
                submission_type
            )

        for comment in comments:
            comment_id = comment['id']

            parent_id_prefix = comment['parent_id'][0:2]
            parent_id = comment['parent_id'][3:]

            # Comment is top-level
            if parent_id_prefix == "t3":
                # Draw top-level comment
                self.addNode(activity_object=comment, Type="Top_comment")

                # Draw influence relation between submissions author and top-level
                self.addEdge(
                    from_ID=submission_id,
                    to_ID=comment_id,
                    score=comment["upvotes"]
                )

            # Comment is a subcomment
            elif parent_id_prefix == "t1":
                # Draw subcomment
                self.addNode(activity_object=comment, Type="Subcomment")

                parent_comment = self.mongo_db_connector.getCommentInfo(
                    comment_id=parent_id,
                    Type=submission_type
                )

                # Draw influence relation between parent commenters and child commenters
                self.addEdge(
                    from_ID=parent_comment["id"],
                    to_ID=comment_id,
                    score=comment["upvotes"]
                )
