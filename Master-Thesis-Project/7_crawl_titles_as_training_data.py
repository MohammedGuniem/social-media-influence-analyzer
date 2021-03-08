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

topic_subreddits_mapping = {
    "comedy": ["comedy", "funny", "comedyheaven"],
    "politics": ["politics", "PoliticsPeopleTwitter", "elections"],
    "sport": ["sports", "football", "basketball"]
}

data = {"training_data": []}
for category, subreddits in topic_subreddits_mapping.items():
    for subreddit in subreddits:
        submissions = crawler.crawlSubmissions(
            subreddits=[{"display_name": subreddit}], submissions_type="New", submission_limit=100)
        for submission in submissions:
            data["training_data"].append({
                "title": submission['title'],
                "label": category
            })

print(F"\n#of titles {len(data)}")

# Database connector
mongo_db_connector = MongoDBConnector(MongoDB_connection_string)

# Deleting test documents from mongoDB
mongo_db_connector.remove_collection(
    "Machine_Learning", "Test_Topic_Detection")

mongo_db_connector.writeToDB(database_name="Machine_Learning",
                             collection_name="Test_Topic_Detection", data=[data])
