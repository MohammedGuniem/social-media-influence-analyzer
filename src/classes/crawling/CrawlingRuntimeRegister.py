import time


class RuntimeRegister:

    def __init__(self, network_name):
        self.timestamp = time.time()
        self.network_name = network_name
        self.groups_count = 0
        self.groups_crawling_time = 0
        self.submissions_type = ""
        self.submissions_count = 0
        self.submissions_crawling_time = 0
        self.comments_count = 0
        self.comments_crawling_time = 0
        self.training_submissions_type = ""
        self.training_submissions_count = 0
        self.training_submissions_crawling_time = 0

    def getRunningTime(self):
        return {
            "timestamp": round(self.timestamp),
            "network_name": self.network_name,
            "groups_count": self.groups_count,
            "groups_crawling_time": round(self.groups_crawling_time),
            "submissions_type": self.submissions_type,
            "submissions_count": self.submissions_count,
            "submissions_crawling_time": round(self.submissions_crawling_time),
            "comments_count": self.comments_count,
            "comments_crawling_time": round(self.comments_crawling_time),
            "training_submissions_type": self.training_submissions_type,
            "training_submissions_count": self.training_submissions_count,
            "training_submissions_crawling_time": self.training_submissions_crawling_time
        }
