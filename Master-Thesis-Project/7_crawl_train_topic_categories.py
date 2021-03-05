import sys
from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.crawling.RedditCrawlClass import RedditCrawler
from dotenv import load_dotenv
from datetime import date
import string
import os


def find_common_words(lists):
    common = []
    for i in range(0, len(lists), 1):
        rest = []
        for l in lists[i+1:len(lists)]:
            rest += l
        current_common = list(set(lists[i]) & set(rest))
        common += current_common
    return list(set(common))


load_dotenv()

client_id = os.environ.get('reddit_client_id')
client_secret = os.environ.get('reddit_client_secret')
user_agent = os.environ.get('reddit_user_agent')
username = os.environ.get('reddit_username')
password = os.environ.get('reddit_password')
MongoDB_connection_string = os.environ.get('mongo_connnection_string')

crawler = RedditCrawler(
    client_id, client_secret, user_agent, username, password)

topic_subreddits_mapping = {
    "comedy": ["comedy", "funny", "comedyheaven"],
    "politics": ["politics", "PoliticsPeopleTwitter", "elections"],
    "sport": ["football", "basketball", "sports"]
}

data = {}
for category, subreddits in topic_subreddits_mapping.items():
    data[category] = []
    for subreddit in subreddits:
        submissions = crawler.crawlSubmissions(
            subreddits=[{"display_name": subreddit}], submissions_type="New", submission_limit=3)
        for submission in submissions:
            split_words = (submission['title']).split(" ")
            for word in split_words:
                data[category].append([word])

print(
    F"\n#of words after before removing duplicates {sum(len(r) for r in data.values())}")

"""
# detecting duplicate words between categories
common = find_common_words(words)
print(F"#of duplicate words {len(common)}")

# removing duplicate words between categories
for category_words in words:
    for word in category_words:
        if word in common:
            category_words.remove(word)
print(F"#of words after removing duplicates {sum(len(r) for r in words)}")
"""

# Database connector
mongo_db_connector = MongoDBConnector(MongoDB_connection_string)

# Deleting test documents from mongoDB
mongo_db_connector.remove_collection(
    "Train_Topic_Detection", str(date.today()))

mongo_db_connector.writeToDB(database_name="Train_Topic_Detection", collection_name=str(
    date.today()), data=[data])
