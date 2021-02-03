from classes.crawling.NewRedditCrawlClass import NewRedditCrawler
from classes.database_connectors.MongoDBConnector import MongoDBConnector
from dotenv import load_dotenv
from datetime import date
import os

load_dotenv()

client_id = os.environ.get('reddit_client_id')
client_secret = os.environ.get('reddit_client_secret')
user_agent = os.environ.get('reddit_user_agent')
username = os.environ.get('reddit_username')
password = os.environ.get('reddit_password')
MongoDB_connection_string = os.environ.get('mongo_connnection_string')

redditCrawler = NewRedditCrawler(
    client_id, client_secret, user_agent, username, password)

# A limit for the number of subreddits to crawl
subreddit_limit = 3

# A limit for the number of submissions to crawl
submission_limit = 1

users = []
# Target Subreddits (subreddit_limit? Most pupolar)
subreddits_info, users_info = redditCrawler.crawlPopularSubreddits(
    subreddit_limit=subreddit_limit)
users += users_info
print("#subreddits: ", len(subreddits_info))
print("#users: ", len(users))
print("-----------------------")

submissions = []
for subreddit in subreddits_info:
    submissions_info, users_info = redditCrawler.crawlSubmissions(
        subreddit['display_name'], Type="New", submission_limit=submission_limit)
    submissions += submissions_info
    users += users_info
print("#submissions: ", len(submissions))
print("#users: ", len(users))
print("-----------------------")

comments = []
for submission in submissions_info:
    comments_info, users_info = redditCrawler.crawlComments(
        submission_id=submission['id'])
    comments += comments_info
    users += users_info
print("#comments: ", len(comments))
print("#users: ", len(users))
print("-----------------------")
print(users[len(users)-1])
