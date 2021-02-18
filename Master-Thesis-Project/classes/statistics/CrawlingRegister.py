from datetime import date


class CrawlingRegister:

    def __init__(self):
        self.crawling_start = 0
        self.crawling_end = 0
        self.total_crawling_time = 0
        self.subreddits_num = 0
        self.subreddits_total_runtime = 0
        self.subreddits_runtimes = {}

        self.subreddit_events = {}

    def set_crawling_start(self, crawling_start_time):
        self.crawling_start = crawling_start_time

    def set_crawling_end(self, crawling_end_time):
        self.crawling_end = crawling_end_time
        self.total_crawling_time = self.crawling_end - self.crawling_start

    def set_subreddits_num(self, number_of_crawled_subreddits):
        self.subreddits_num = number_of_crawled_subreddits

    def set_subreddits_total_runtime(self, runtime):
        self.subreddits_total_runtime = runtime

    def set_subreddit_runtime(self, subreddit_id, runtime):
        self.subreddits_runtimes[str(subreddit_id)] = runtime

    def add_submissions_type(self, submissions_type):
        self.subreddit_events[submissions_type] = {
            "submissions_num": 0,
            "comments_num": 0,
            "users_num": 0,
            "submissions_total_runtime": 0,
            "comments_total_runtime": 0,
            "submissions_runtimes": {},
            "comments_runtimes": {},
        }

    def set_submissions_num(self, number_of_crawled_submissions, submissions_type):
        self.subreddit_events[submissions_type]["submissions_num"] = number_of_crawled_submissions

    def set_comments_num(self, number_of_crawled_comments, submissions_type):
        self.subreddit_events[submissions_type]["comments_num"] = number_of_crawled_comments

    def update_users_num(self, number_of_crawled_users, submissions_type):
        self.subreddit_events[submissions_type]["users_num"] += number_of_crawled_users

    def set_submissions_total_runtime(self, runtime, submissions_type):
        self.subreddit_events[submissions_type]["submissions_total_runtime"] = runtime

    def set_comments_total_runtime(self, runtime, submissions_type):
        self.subreddit_events[submissions_type]["comments_total_runtime"] = runtime

    def set_submission_runtime(self, submission_id, runtime, submissions_type):
        self.subreddit_events[submissions_type]["submissions_runtimes"][str(
            submission_id)] = runtime

    def set_comment_runtime(self, comment_id, runtime, submissions_type):
        self.subreddit_events[submissions_type]["comments_runtimes"][str(
            comment_id)] = runtime

    def get_running_times(self):
        running_time_data = {
            "crawling_start": self.crawling_end,
            "crawling_end": self.crawling_end,
            "total_crawling_time": self.total_crawling_time,
            "subreddits_num": self.subreddits_num,
            "subreddits_total_runtime": self.subreddits_total_runtime,
            "subreddits_runtimes": self.subreddits_runtimes,
            "subreddit_events": self.subreddit_events
        }
        return running_time_data
