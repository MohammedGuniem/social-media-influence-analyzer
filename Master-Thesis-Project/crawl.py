from classes.crawling.RedditCrawlClass import RedditCrawler
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

redditCrawler = RedditCrawler(
    client_id, client_secret, user_agent, username, password)

# A limit for the number of subreddits to crawl
subreddit_limit = 3

# A limit for the number of submissions to crawl
submission_limit = 33

# Database connector
MongoDBConnector = MongoDBConnector(MongoDB_connection_string)

# Target Subreddits (subreddit_limit? Most pupolar)
subreddits_info, running_times = redditCrawler.crawlPopularSubreddits(
    subreddit_limit=subreddit_limit)
print("#subreddits: ", len(subreddits_info))
print("-----------------------")

MongoDBConnector.writeToMongoDB(
    database_name="Subreddits_DB", collection_name=str(date.today()), data=subreddits_info)

execution_times = {
    "subreddits": running_times,
    "submissions": {},
    "comments": {}
}
# , "Top", "Hot"
for Type in ["New", "Rising"]:
    print(F"Crawling {Type} Submissions...")
    submissions, users = [], []
    for subreddit in subreddits_info:
        submissions_info, users_info, running_times = redditCrawler.crawlSubmissions(
            subreddit['display_name'], Type=Type, submission_limit=submission_limit)
        submissions += submissions_info
        users += users_info
        print("#users: ", len(users_info))
    print("#submissions: ", len(submissions))

    execution_times["submissions"][Type] = running_times

    MongoDBConnector.writeToMongoDB(
        database_name=F"{Type}_Submissions_DB", collection_name=str(date.today()), data=submissions)

    comments = []
    for submission in submissions_info:
        comments_info, users_info, running_times = redditCrawler.crawlComments(
            submission_id=submission['id'])
        comments += comments_info
        users += users_info
        print("#users: ", len(users_info))
    print("#comments: ", len(comments))

    MongoDBConnector.writeToMongoDB(
        database_name=F"{Type}_Comments_DB", collection_name=str(date.today()), data=comments)

    MongoDBConnector.writeToMongoDB(
        database_name=F"{Type}_Users_DB", collection_name=str(date.today()), data=users)

    execution_times["comments"][Type] = running_times

MongoDBConnector.writeToMongoDB(
    database_name="admin", collection_name=str(date.today()), data=[{"id": redditCrawler.getTimeStamp(), "execution_times": execution_times}])
