from classes.crawling.CrawlingRuntimeRegister import RuntimeRegister
import time
import json

class TestCrawler:

    def __init__(self, test_data_path):
        self.test_data_path = test_data_path
        self.runtime_register = RuntimeRegister("Test")

    # Method to crawl groups information.
    def getGroups(self):
        start = time.time()
        dummy_groups = []
        with open(F'{self.test_data_path}/groups.json', encoding="utf8") as groups_file:
            dummy_groups = json.load(groups_file)
        self.runtime_register.groups_count = len(dummy_groups)
        self.runtime_register.groups_crawling_time = time.time() - start
        return dummy_groups

    # Method to crawl submissions information.
    def getSubmissions(self):
        start = time.time()
        dummy_submissions = []
        with open(F'{self.test_data_path}/submissions.json', encoding="utf8") as submissions_file:
            dummy_submissions = json.load(submissions_file)
        self.runtime_register.submissions_type = "New"
        self.runtime_register.submissions_count = len(dummy_submissions)
        self.runtime_register.submissions_crawling_time = time.time() - start
        return dummy_submissions

    # Method to crawl comments information.
    def getComments(self):
        start = time.time()
        dummy_comments = []
        with open(F'{self.test_data_path}/comments.json', encoding="utf8") as comments_file:
            dummy_comments = json.load(comments_file)
        self.runtime_register.comments_count = len(dummy_comments)
        self.runtime_register.comments_crawling_time = time.time() - start
        return dummy_comments

    # Method to crawl trainingdata to enable topic classification of a certain submission
    def getInfluenceAreaTrainingData(self):
        start = time.time()
        dummy_training_data = []
        with open(F'{self.test_data_path}/topic_training_data.json', encoding="utf8") as topic_training_data_file:
            dummy_training_data = json.load(topic_training_data_file)
        data = {
            "training_data": dummy_training_data
        }
        self.runtime_register.training_submissions_type = "New"
        self.runtime_register.training_submissions_count = len(data["training_data"])
        self.runtime_register.training_submissions_crawling_time = time.time() - start
        return data
