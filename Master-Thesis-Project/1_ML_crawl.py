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
    "politic": ["politics", "PoliticsPeopleTwitter", "elections"],
    "economy": ["Economics", "economy", "business"],
    "sport": ["sports", "olympics", "worldcup"],
    "entertainment": ["movies", "comedy", "culture"],
    "technology": ["technology", "science", "Futurology"]
}

data = {"training_data": []}
for category, subreddits in topic_subreddits_mapping.items():
    for subreddit in subreddits:
        submissions = crawler.getSubmissionsTitles(
            subreddits=[{"display_name": subreddit}], submissions_type="New", submission_limit=100)
        for submission_title in submissions:
            data["training_data"].append({
                "title": submission_title,
                "label": category
            })

print(F"\n#of titles {len(data)}")

# Database connector
mongo_db_connector = MongoDBConnector(MongoDB_connection_string)

# Deleting test documents from mongoDB
mongo_db_connector.remove_collection(
    "Text_Classification_Training_Data", str(date.today()))

mongo_db_connector.writeToDB(database_name="Text_Classification_Training_Data",
                             collection_name=str(date.today()), data=[data])
