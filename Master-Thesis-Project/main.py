from RedditCrawlClass import RedditCrawler
from dotenv import load_dotenv
import pymongo
import os

load_dotenv()

client_id = os.environ.get('reddit_client_id')
client_secret = os.environ.get('reddit_client_secret')
user_agent = os.environ.get('reddit_user_agent')
username = os.environ.get('reddit_username')
password = os.environ.get('reddit_password')
mongo_connection_string = os.environ.get('mongo_connnection_string')

def importToMongoDB(connection_string, database_name, collection_name, data):
    client = pymongo.MongoClient(connection_string)
    database = client[database_name]
    collection = database[collection_name]
    for entry in data:
        # Insert or update using the upsert option set to True
        result = collection.update({'id':entry['id']}, entry, True)

redditCrawler = RedditCrawler(client_id, client_secret, user_agent, username, password)

subreddits, extracted_users = redditCrawler.crawlSubreddits(Type="Popular", limit=3)
print(F"Number of crawled subreddits: {len(subreddits)}, with {len(extracted_users)} crawled user(s)")

importToMongoDB(mongo_connection_string, database_name="Subreddits", collection_name="Popular", data=subreddits)

importToMongoDB(mongo_connection_string, database_name="Users", collection_name="ALL", data=extracted_users)

submissions = []
submissions_authors = []
for subreddit in subreddits:
    subreddit_submissions, extracted_users = redditCrawler.crawlSubmissions(subreddit["display_name"], 3)
    submissions += subreddit_submissions
    submissions_authors += extracted_users
print(F"Number of crawled submissions: {len(submissions)}, with {len(submissions_authors)} crawled user(s)")

importToMongoDB(mongo_connection_string, database_name="Submissions", collection_name="New", data=submissions)

importToMongoDB(mongo_connection_string, database_name="Users", collection_name="ALL", data=submissions_authors)

comments = []
comments_authors = []
for submission in submissions:
    submission_comments, extracted_users = redditCrawler.crawlComments(submission["id"])
    comments += submission_comments
    comments_authors += extracted_users
print(F"Number of crawled comments: {len(comments)}, with {len(comments_authors)} crawled user(s)")

importToMongoDB(mongo_connection_string, database_name="Comments", collection_name="ALL", data=comments)

importToMongoDB(mongo_connection_string, database_name="Users", collection_name="ALL", data=comments_authors)

