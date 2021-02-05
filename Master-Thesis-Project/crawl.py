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
submission_limit = 3

# Type of submissions to crawl
Types = []
Types.append("New")
Types.append("Rising")
# Types.append("Hot")
# Types.append("Top")

# Database connector
MongoDBConnector = MongoDBConnector(MongoDB_connection_string)

execution_time_data = {
    "start_time": redditCrawler.getTimeStamp(),
    "subreddits": [],
    "submissions": [],
    "comments": [],
    "__total__subreddits": {},
    "__total__submissions": {},
    "__total__comments": {},
}

# Target Subreddits (subreddit_limit? Most pupolar)
subreddits_info, execution_time = redditCrawler.crawlPopularSubreddits(
    subreddit_limit=subreddit_limit)
execution_time_data["subreddits"] += execution_time[0]
execution_time_data["__total__subreddits"] = execution_time[1]
print("#subreddits: ", len(subreddits_info))
print("-----------------------")

MongoDBConnector.writeToMongoDB(
    database_name="Subreddits_DB", collection_name=str(date.today()), data=subreddits_info)

for Type in Types:
    print(F"Crawling {Type} Submissions...")
    submissions, users = [], []
    for subreddit in subreddits_info:
        submissions_info, users_info, execution_time = redditCrawler.crawlSubmissions(
            subreddit['display_name'], Type=Type, submission_limit=submission_limit)
        execution_time_data["submissions"] += execution_time[0]
        execution_time_data["__total__submissions"][subreddit['id']
                                                    ] = execution_time[1]
        submissions += submissions_info
        users += users_info

        print("#users: ", len(users_info))
    print("#submissions: ", len(submissions))

    MongoDBConnector.writeToMongoDB(
        database_name=F"{Type}_Submissions_DB", collection_name=str(date.today()), data=submissions)

    comments = []
    for submission in submissions_info:
        comments_info, users_info, execution_time = redditCrawler.crawlComments(
            submission_id=submission['id'])
        comments += comments_info
        users += users_info
        execution_time_data["comments"] += execution_time[0]
        execution_time_data["__total__comments"][submission['id']
                                                 ] = execution_time[1]
        print("#users: ", len(users_info))
    print("#comments: ", len(comments))

    MongoDBConnector.writeToMongoDB(
        database_name=F"{Type}_Comments_DB", collection_name=str(date.today()), data=comments)

    MongoDBConnector.writeToMongoDB(
        database_name=F"{Type}_Users_DB", collection_name=str(date.today()), data=users)

execution_time_data['end_time'] = redditCrawler.getTimeStamp()
execution_time_data['id'] = F"{execution_time_data['start_time']}_{redditCrawler.getTimeStamp()}"
MongoDBConnector.writeToMongoDB(
    database_name="admin", collection_name=str(date.today()), data=[execution_time_data])
