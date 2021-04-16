from classes.crawling.CrawlingRuntimeRegister import RuntimeRegister
import time


class TestCrawler:

    def __init__(self):
        self.runtime_register = RuntimeRegister("Test")

    # Method to crawl groups information.
    def getGroups(self):
        start = time.time()
        dummy_groups = [
            {
                "id": "Test_1",
                "display_name": "Economy_and_Politic_Group"
            },
            {
                "id": "Test_2",
                "display_name": "Sport_and_Technology_Group"
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
                "group_id": "Test_1",
                "body": "Tech giant invests 30 billions in renewable energy",
                "upvotes": 10
            },
            {
                "id": "S_2",
                "author_id": "U_2",
                "author_name": "User B",
                "num_comments": 3,
                "group_id": "Test_1",
                "body": "If only America could have short election cycles like near everywhere else",
                "upvotes": 3
            },
            {
                "id": "S_3",
                "author_id": "U_3",
                "author_name": "User C",
                "num_comments": 5,
                "group_id": "Test_2",
                "body": "100 days to go until Tokyo 2020",
                "upvotes": 10
            },
            {
                "id": "S_4",
                "author_id": "U_3",
                "author_name": "User C",
                "num_comments": 1,
                "group_id": "Test_2",
                "body": "Kroger Is Amassing A Robot Army To Battle Amazon, Walmart",
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
                "body": "not much",
                "parent_id": "t3_S_1",
                "submission_id": "t3_S_1",
                "group_id": "Test_1",
                "upvotes": 7
            },
            {
                "id": "SC_1",
                "author_id": "U_1",
                "author_name": "User A",
                "body": "ok",
                "parent_id": "t1_TC_1",
                "submission_id": "t3_S_1",
                "group_id": "Test_1",
                "upvotes": 2
            },
            {
                "id": "SC_2",
                "author_id": "U_1",
                "author_name": "User A",
                "body": "You want to play tennis?",
                "parent_id": "t1_TC_1",
                "submission_id": "t3_S_1",
                "group_id": "Test_1",
                "upvotes": 3
            },
            {
                "id": "SC_3",
                "author_id": "U_4",
                "author_name": "User D",
                "body": "Sure",
                "parent_id": "t1_SC_2",
                "submission_id": "t3_S_1",
                "group_id": "Test_1",
                "upvotes": 8
            },
            {
                "id": "TC_2",
                "author_id": "U_5",
                "author_name": "User E",
                "body": "amazing",
                "parent_id": "t3_S_2",
                "submission_id": "t3_S_2",
                "group_id": "Test_1",
                "upvotes": 9
            },
            {
                "id": "TC_3",
                "author_id": "U_6",
                "author_name": "User F",
                "body": "You want to go running?",
                "parent_id": "t3_S_2",
                "submission_id": "t3_S_2",
                "group_id": "Test_1",
                "upvotes": 5
            },
            {
                "id": "SC_4",
                "author_id": "U_2",
                "author_name": "User B",
                "body": "No, thanks",
                "parent_id": "t1_TC_3",
                "submission_id": "t3_S_2",
                "group_id": "Test_1",
                "upvotes": 8
            },
            {
                "id": "TC_4",
                "author_id": "U_6",
                "author_name": "User F",
                "body": "Not me",
                "parent_id": "t3_S_3",
                "submission_id": "t3_S_3",
                "group_id": "Test_2",
                "upvotes": 7
            },
            {
                "id": "TC_5",
                "author_id": "U_7",
                "author_name": "User G",
                "body": "me too",
                "parent_id": "t3_S_3",
                "submission_id": "t3_S_3",
                "group_id": "Test_2",
                "upvotes": 5
            },
            {
                "id": "TC_6",
                "author_id": "U_6",
                "author_name": "User F",
                "body": "I like cake",
                "parent_id": "t3_S_3",
                "submission_id": "t3_S_3",
                "group_id": "Test_2",
                "upvotes": 10
            },
            {
                "id": "SC_5",
                "author_id": "U_3",
                "author_name": "User C",
                "body": "that what i thought",
                "parent_id": "t1_TC_5",
                "submission_id": "t3_S_3",
                "group_id": "Test_2",
                "upvotes": 3
            },
            {
                "id": "SC_6",
                "author_id": "U_3",
                "author_name": "User C",
                "body": "you are a cool person",
                "parent_id": "t1_TC_5",
                "submission_id": "t3_S_3",
                "group_id": "Test_2",
                "upvotes": 10
            },
            {
                "id": "TC_7",
                "author_id": "U_6",
                "author_name": "User F",
                "body": "Yes it is",
                "parent_id": "t3_S_4",
                "submission_id": "t3_S_4",
                "group_id": "Test_2",
                "upvotes": 2
            }
        ]
        self.runtime_register.comments_count = len(dummy_comments)
        self.runtime_register.comments_crawling_time = time.time() - start
        return dummy_comments
