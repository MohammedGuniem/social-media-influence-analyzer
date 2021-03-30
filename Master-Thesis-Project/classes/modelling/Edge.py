class Edge:
    def __init__(self, from_node_id, relation_type, to_node_id, influence_areas, group_names, interaction_score, activity_score, upvotes_score):
        self.from_node = from_node_id
        self.relation_type = relation_type
        self.to_node = to_node_id
        self.interaction_score = 0
        self.activity_score = 0
        self.upvotes = 0
        self.scores = {
            'interaction': self.interaction_score,
            'activity': self.activity_score,
            'upvotes': self.upvotes,
            'interaction_and_activity': self.interaction_score + self.activity_score,
            'interaction_and_upvotes': self.interaction_score + self.upvotes,
            'activity_and_upvotes': self.activity_score + self.upvotes,
            'total': self.interaction_score + self.activity_score + self.upvotes
        }

        self.influence_areas = influence_areas
        self.group_names = group_names

    def updateScore(self, interaction_score, activity_score, upvotes_score):
        scores = self.scores
        scores['interaction'] += interaction_score
        scores['activity'] += activity_score
        scores['upvotes'] += upvotes_score
        scores['interaction_and_activity'] += interaction_score + activity_score
        scores['interaction_and_upvotes'] += interaction_score + upvotes_score
        scores['activity_and_upvotes'] += activity_score + upvotes_score
        scores['total'] += interaction_score + activity_score + upvotes_score
        self.scores = scores
