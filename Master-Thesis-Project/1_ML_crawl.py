import sys
from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.crawling.RedditCrawlClass import RedditCrawler
from dotenv import load_dotenv
from datetime import date
import string
import os

load_dotenv()

# Reddit crawler
crawler = RedditCrawler(
    client_id=os.environ.get('reddit_client_id'),
    client_secret=os.environ.get('reddit_client_secret'),
    user_agent=os.environ.get('reddit_user_agent'),
    username=os.environ.get('reddit_username'),
    password=os.environ.get('reddit_password')
)

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

# Mongo db database connector
mongo_db_connector = MongoDBConnector(
    host=os.environ.get('mongo_db_host'),
    port=int(os.environ.get('mongo_db_port')),
    user=os.environ.get('mongo_db_user'),
    passowrd=os.environ.get('mongo_db_pass')
)

# Deleting test documents from mongoDB
mongo_db_connector.remove_collection(
    "Text_Classification_Training_Data", str(date.today()))

mongo_db_connector.writeToDB(database_name="Text_Classification_Training_Data",
                             collection_name=str(date.today()), data=[data])
