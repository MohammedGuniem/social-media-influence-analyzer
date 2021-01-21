from RedditCrawlClass import RedditCrawler
from dotenv import load_dotenv
from pymongo import UpdateOne
from datetime import date
import pymongo
import os

load_dotenv()

client_id = os.environ.get('reddit_client_id')
client_secret = os.environ.get('reddit_client_secret')
user_agent = os.environ.get('reddit_user_agent')
username = os.environ.get('reddit_username')
password = os.environ.get('reddit_password')
mongo_connection_string = os.environ.get('mongo_connnection_string')

def writeToMongoDB(connection_string, database_name, collection_name, data):
    client = pymongo.MongoClient(connection_string)
    database = client[database_name]
    collection = database[collection_name]
    requests = []
    for entry in data:
        # Insert or update using the upsert option set to True
        requests.append(UpdateOne({"id":entry['id']}, {"$set": entry}, upsert=True))
    collection.bulk_write(requests)

redditCrawler = RedditCrawler(client_id, client_secret, user_agent, username, password)

database_name = str(date.today())

subreddits, extracted_users = redditCrawler.crawlSubreddits(Type="Popular", limit=3)
print(F"Number of crawled subreddits: {len(subreddits)}, with {len(extracted_users)} crawled user(s)")

writeToMongoDB(mongo_connection_string, database_name=database_name, collection_name="Popular Subreddits", data=subreddits)
writeToMongoDB(mongo_connection_string, database_name=database_name, collection_name="New Users", data=extracted_users)

submissions = []
submissions_authors = []
for subreddit in subreddits:
    subreddit_submissions, extracted_users, subreddit_flairs = redditCrawler.crawlSubmissions(subreddit["display_name"], 3)
    submissions += subreddit_submissions
    submissions_authors += extracted_users
print(F"Number of crawled submissions: {len(submissions)}, with {len(submissions_authors)} crawled user(s)")

writeToMongoDB(mongo_connection_string, database_name=database_name, collection_name="New Submissions", data=submissions)
writeToMongoDB(mongo_connection_string, database_name=database_name, collection_name="New Users", data=submissions_authors)

comments = []
comments_authors = []
for submission in submissions:
    submission_comments, extracted_users = redditCrawler.crawlComments(submission["id"])
    comments += submission_comments
    comments_authors += extracted_users
print(F"Number of crawled comments: {len(comments)}, with {len(comments_authors)} crawled user(s)")

writeToMongoDB(mongo_connection_string, database_name=database_name, collection_name="New Comments", data=comments)
writeToMongoDB(mongo_connection_string, database_name=database_name, collection_name="New Users", data=comments_authors)
