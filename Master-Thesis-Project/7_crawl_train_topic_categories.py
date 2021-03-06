import copy
import sys
from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.crawling.RedditCrawlClass import RedditCrawler
from dotenv import load_dotenv
from datetime import date
import string
import os

load_dotenv()

client_id = os.environ.get('reddit_client_id')
client_secret = os.environ.get('reddit_client_secret')
user_agent = os.environ.get('reddit_user_agent')
username = os.environ.get('reddit_username')
password = os.environ.get('reddit_password')
MongoDB_connection_string = os.environ.get('mongo_connnection_string')

crawler = RedditCrawler(
    client_id, client_secret, user_agent, username, password)


def clean_text(input_text):
    alphabet = list(string.ascii_lowercase)
    numbers = [str(num) for num in range(0, 10, 1)]
    output_text = ""
    for char in input_text.lower():
        if (char == " ") or (char in alphabet) or (char in numbers):
            output_text += char
    return output_text


topic_subreddits_mapping = {
    "comedy": ["funny", "comedyheaven"],
    "politics": ["PoliticsPeopleTwitter", "elections"],
    "sport": ["football", "basketball"]
}

data = {}
for category, subreddits in topic_subreddits_mapping.items():
    data[category] = []
    for subreddit in subreddits:
        submissions = crawler.crawlSubmissions(
            subreddits=[{"display_name": subreddit}], submissions_type="New", submission_limit=100)
        for submission in submissions:
            split_words = (clean_text(submission['title'])).split(" ")
            for word in split_words:
                data[category].append([word])

# detecting and removing duplicate words between categories


def remove_duplicates(d):
    black_list = []
    for k1, v1 in d.items():
        for k2, v2 in d.items():
            if k1 != k2:
                for item in v1:
                    if (item in v2) or (item in black_list):
                        v1.remove(item)
                        black_list.append(item)
    return d


unique_words_data = remove_duplicates(copy.deepcopy(data))
print(
    F"\n#of words after before removing duplicates {sum(len(r) for r in data.values())}")

print(
    F"#of words after removing duplicates {sum(len(r) for r in unique_words_data.values())}")

# Database connector
mongo_db_connector = MongoDBConnector(MongoDB_connection_string)

# Deleting test documents from mongoDB
mongo_db_connector.remove_collection(
    "Machine_Learning", "Train_Topic_Detection_All")

mongo_db_connector.remove_collection(
    "Machine_Learning", "Train_Topic_Detection_Unique")

# Inserting new documents
mongo_db_connector.writeToDB(database_name="Machine_Learning",
                             collection_name="Train_Topic_Detection_All", data=[data])

mongo_db_connector.writeToDB(database_name="Machine_Learning",
                             collection_name="Train_Topic_Detection_Unique", data=[unique_words_data])
