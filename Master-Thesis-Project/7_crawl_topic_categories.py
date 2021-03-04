import sys
from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.crawling.RedditCrawlClass import RedditCrawler
from dotenv import load_dotenv
from datetime import date
import string
import os

# prepare


def get_letters_mapping():
    mapping = {}
    alphabet = list(string.printable)
    for letter in alphabet:
        mapping[letter] = ord(letter)
    return mapping


def encode(text):
    mybytes = text.encode('utf-8')
    myint = int.from_bytes(mybytes, 'little')
    return myint


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

words = []
categories = []
for category, subreddits in topic_subreddits_mapping.items():
    category_words = []
    for subreddit in subreddits:
        submissions = crawler.crawlSubmissions(
            subreddits=[{"display_name": subreddit}], submissions_type="New", submission_limit=1)
        for submission in submissions:
            split_words = (submission['title']).split(" ")
            category_words += split_words

    words.append(category_words)
    categories.append(category)

print(F"\n#of words after before duplicates {sum(len(r) for r in words)}")

# detecting duplicate words between categories
common = find_common_words(words)
print(F"#of duplicate words {len(common)}")

# removing duplicate words between categories
for category_words in words:
    for word in category_words:
        if word in common:
            category_words.remove(word)
print(F"#of words after removing duplicates {sum(len(r) for r in words)}")

data = {
    "words": [],
    "encoded_words": [],
    "topic": [],
    "encoded_topic": []
}

for index in range(0, len(words), 1):
    category = categories[index]
    for word in words[index]:
        data["words"].append(word)
        data["encoded_words"].append(encode(word))
        data["topic"].append(category)
        data["encoded_topic"].append(encode(category))

# Database connector
mongo_db_connector = MongoDBConnector(MongoDB_connection_string)

# Deleting test documents from mongoDB
mongo_db_connector.remove_collection("Topic_Detection_New", str(date.today()))

mongo_db_connector.writeToDB(database_name="Topic_Detection_New", collection_name=str(
    date.today()), data=[data])
