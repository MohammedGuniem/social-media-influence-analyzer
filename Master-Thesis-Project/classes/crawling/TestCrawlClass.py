from classes.crawling.CrawlingRuntimeRegister import RuntimeRegister
import time


class TestCrawler:

    def __init__(self):
        self.runtime_register = RuntimeRegister("Test Network")

    # Method to crawl groups information.
    def getGroups(self):
        start = time.time()
        dummy_groups = [
            {
                "id": "Test",
                "display_name": "Test"
            },
            {
                "id": "Test_2",
                "display_name": "Test_2"
            }
        ]
        self.runtime_register.groups_count = len(dummy_groups)
        self.runtime_register.groups_crawling_time = time.time() - start
        return dummy_groups

    # Method to crawl submissions information.
    def getSubmissions(self):
        start = time.time()
        dummy_submissions = [
            {
                "id": "S_1",
                "author_id": "U_1",
                "author_name": "User A",
                "num_comments": 4,
                "subreddit_id": "Test",
                "title": "What's up?",
                "upvotes": 10
            },
            {
                "id": "S_2",
                "author_id": "U_2",
                "author_name": "User B",
                "num_comments": 3,
                "subreddit_id": "Test",
                "title": "What a lovely day!",
                "upvotes": 3
            },
            {
                "id": "S_3",
                "author_id": "U_3",
                "author_name": "User C",
                "num_comments": 5,
                "subreddit_id": "Test",
                "title": "Who likes icecream?",
                "upvotes": 10
            },
            {
                "id": "S_4",
                "author_id": "U_3",
                "author_name": "User C",
                "num_comments": 1,
                "subreddit_id": "Test_2",
                "title": "What a lovely day!",
                "upvotes": 7
            }
        ]
        self.runtime_register.submissions_type = "New"
        self.runtime_register.submissions_count = len(dummy_submissions)
        self.runtime_register.submissions_crawling_time = time.time() - start
        return dummy_submissions

    # Method to crawl comments information.
    def getComments(self):
        start = time.time()
        dummy_comments = [
            {
                "id": "TC_1",
                "author_id": "U_4",
                "author_name": "User D",
                "comment_body": "not much",
                "parent_id": "t3_S_1",
                "submission_id": "t3_S_1",
                "subreddit_id": "Test",
                "upvotes": 7
            },
            {
                "id": "SC_1",
                "author_id": "U_1",
                "author_name": "User A",
                "comment_body": "ok",
                "parent_id": "t1_TC_1",
                "submission_id": "t3_S_1",
                "subreddit_id": "Test",
                "upvotes": 2
            },
            {
                "id": "SC_2",
                "author_id": "U_1",
                "author_name": "User A",
                "comment_body": "You want to play tennis?",
                "parent_id": "t1_TC_1",
                "submission_id": "t3_S_1",
                "subreddit_id": "Test",
                "upvotes": 3
            },
            {
                "id": "SC_3",
                "author_id": "U_4",
                "author_name": "User D",
                "comment_body": "Sure",
                "parent_id": "t1_SC_2",
                "submission_id": "t3_S_1",
                "subreddit_id": "Test",
                "upvotes": 8
            },
            {
                "id": "TC_2",
                "author_id": "U_5",
                "author_name": "User E",
                "comment_body": "amazing",
                "parent_id": "t3_S_2",
                "submission_id": "t3_S_2",
                "subreddit_id": "Test",
                "upvotes": 9
            },
            {
                "id": "TC_3",
                "author_id": "U_6",
                "author_name": "User F",
                "comment_body": "You want to go running?",
                "parent_id": "t3_S_2",
                "submission_id": "t3_S_2",
                "subreddit_id": "Test",
                "upvotes": 5
            },
            {
                "id": "SC_4",
                "author_id": "U_2",
                "author_name": "User B",
                "comment_body": "No, thanks",
                "parent_id": "t1_TC_3",
                "submission_id": "t3_S_2",
                "subreddit_id": "Test",
                "upvotes": 8
            },
            {
                "id": "TC_4",
                "author_id": "U_6",
                "author_name": "User F",
                "comment_body": "Not me",
                "parent_id": "t3_S_3",
                "submission_id": "t3_S_3",
                "subreddit_id": "Test",
                "upvotes": 7
            },
            {
                "id": "TC_5",
                "author_id": "U_7",
                "author_name": "User G",
                "comment_body": "me too",
                "parent_id": "t3_S_3",
                "submission_id": "t3_S_3",
                "subreddit_id": "Test",
                "upvotes": 5
            },
            {
                "id": "TC_6",
                "author_id": "U_6",
                "author_name": "User F",
                "comment_body": "I like cake",
                "parent_id": "t3_S_3",
                "submission_id": "t3_S_3",
                "subreddit_id": "Test",
                "upvotes": 10
            },
            {
                "id": "SC_5",
                "author_id": "U_3",
                "author_name": "User C",
                "comment_body": "that what i thought",
                "parent_id": "t1_TC_5",
                "submission_id": "t3_S_3",
                "subreddit_id": "Test",
                "upvotes": 3
            },
            {
                "id": "SC_6",
                "author_id": "U_3",
                "author_name": "User C",
                "comment_body": "you are a cool person",
                "parent_id": "t1_TC_5",
                "submission_id": "t3_S_3",
                "subreddit_id": "Test",
                "upvotes": 10
            },
            {
                "id": "TC_7",
                "author_id": "U_6",
                "author_name": "User F",
                "comment_body": "Yes it is",
                "parent_id": "t3_S_4",
                "submission_id": "t3_S_4",
                "subreddit_id": "Test_2",
                "upvotes": 2
            }
        ]
        self.runtime_register.comments_count = len(dummy_comments)
        self.runtime_register.comments_crawling_time = time.time() - start
        return dummy_comments
