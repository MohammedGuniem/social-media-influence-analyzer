import datetime import date


class CrawlingRegister:

    def __init__(self, db_connector):
        self.MongoDBConnector = db_connector

        self.crawling_start = 0
        self.crawling_end = 0
        self.subreddits_num = 0
        self.subreddits_total_runtime = 0
        self.subreddits_runtimes = {}

        self.subreddit_events = {}

    def set_crawling_start(self, crawling_start_time):
        self.crawling_start = crawling_start_time

    def set_crawling_end(self, crawling_end_time):
        self.crawling_end = crawling_end_time

    def set_subreddits_num(self, number_of_crawled_subreddits):
        self.subreddits_num = number_of_crawled_subreddits

    def set_subreddits_total_runtime(self, runtime):
        self.subreddits_total_runtime = runtime

    def set_subreddit_runtime(self, subreddit_id, runtime):
        self.subreddits_runtimes[str(subreddit_id)] = runtime

    def set_submission_type(self, submission_type):
        self.subreddit_events[submission_type] = {
            "submissions_num": 0,
            "comments_num": 0,
            "users_num": 0,
            "submissions_total_runtime": 0,
            "comments_total_runtime": 0,
            "users_total_runtime": 0,
            "submissions_runtimes": {},
            "comments_runtimes": {},
            "users_runtimes": {}
        }

    def set_submissions_num(self, number_of_crawled_submissions, submission_type):
        self.subreddit_events[submission_type]["submissions_num"] = number_of_crawled_submissions

    def set_comments_num(self, number_of_crawled_comments, submission_type):
        self.subreddit_events[submission_type]["comments_num"] = number_of_crawled_comments

    def set_users_num(self, number_of_crawled_users, submission_type):
        self.subreddit_events[submission_type]["users_num"] = number_of_crawled_users

    def set_submissions_total_runtime(self, runtime, submission_type):
        self.subreddit_events[submission_type]["submissions_total_runtime"] = runtime

    def set_comments_total_runtime(self, runtime, submission_type):
        self.subreddit_events[submission_type]["comments_total_runtime"] = runtime

    def set_users_total_runtime(self, runtime, submission_type):
        self.subreddit_events[submission_type]["users_total_runtime"] = runtime

    def set_submission_runtime(self, submission_id, runtime, submission_type):
        self.subreddit_events[submission_type]["submission_runtime"][str(
            submission_id)] = runtime

    def set_comment_runtime(self, comment_id, runtime, submission_type):
        self.subreddit_events[submission_type]["comment_runtime"][str(
            comment_id)] = runtime

    def set_user_runtime(self, user_id, runtime, submission_type):
        self.subreddit_events[submission_type]["user_runtime"][str(
            user_id)] = runtime

    def save_runtimes(self):
        execution_time_data = {
            "crawling_start" = self.crawling_end,
            "crawling_end" = self.crawling_end,
            "subreddits_num" = self.subreddits_num,
            "subreddits_total_runtime" = self.subreddits_total_runtime,
            "subreddits_runtimes" = self.subreddits_runtimes,
            "subreddit_events": self.subreddit_events
        }

        self.MongoDBConnector.writeToDB(
            database_name="admin",
            collection_name=str(date.today()),
            data=execution_time_data
        )
