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


def get_category_mapping():
    to_number = {
        "politics": 1,
        "sport": 2,
        "comedy": 3
    }
    to_text = {
        1: "politics",
        2: "sport",
        3: "comedy"
    }
    return to_number, to_text


def encode_category(category):
    to_number, _ = get_category_mapping()
    return to_number[category]


def decode_category(number):
    _, to_text = get_category_mapping()
    return to_text[number]


def encode(text):
    default_length = 10
    mapping = get_letters_mapping()
    text_array = text.lower().split(" ")
    encoded_array = []
    for word in text_array:
        encoded_word = 0
        for letter in word:
            if letter in mapping.keys():
                encoded_word += mapping[letter]
        encoded_array.append(encoded_word)
    return encoded_array


def decode(encoded_array):
    text = ""
    for encoded_letter in encoded_array:
        text += chr(encoded_letter)
    return text


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

training_data = []
for topic, subreddits in topic_subreddits_mapping.items():
    for subreddit in subreddits:
        submissions = crawler.crawlSubmissions(
            subreddits=[{"display_name": subreddit}], submissions_type="New", submission_limit=75)
        for submission in submissions:
            record = {
                'title': submission['title'],
                'encoded_title': encode(submission['title']),
                'topic': topic,
                'encoded_topic': encode_category(topic),
            }
            training_data.append(record)

# Database connector
mongo_db_connector = MongoDBConnector(MongoDB_connection_string)

# Deleting test documents from mongoDB
mongo_db_connector.remove_collection("Topic_detection", str(date.today()))

mongo_db_connector.writeToDB(database_name="Topic_detection", collection_name=str(
    date.today()), data=training_data)
