from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.statistics.CrawlingRegister import CrawlingRegister
from classes.crawling.RedditCrawlClass import RedditCrawler
from classes.statistics.RunningTime import Timer
from dotenv import load_dotenv
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

# Crawling Runtime Register
register = CrawlingRegister(MongoDBConnector)

# Clock timer
timer = Timer()
start_time = timer.tic()
register.set_crawling_start(start_time)

# Target Subreddits (subreddit_limit? Most pupolar)
subreddits_info, execution_time = crawler.crawlPopularSubreddits(
    subreddit_limit=subreddit_limit
)
execution_time_data["subreddits"] += execution_time[0]
execution_time_data["__total__subreddits"] = execution_time[1]

subreddits_num = len(subreddits_info)
register.set_subreddits_num(number_of_crawled_subreddits=subreddits_num)
register.set_subreddits_total_runtime(runtime=timer.toc())
register.set_subreddit_runtime
print("#subreddits: ", subreddits_num)
print("-----------------------------")

MongoDBConnector.writeToDB(
    database_name="Subreddits_DB", collection_name=str(date.today()), data=subreddits_info)

for Type in Types:
    print(F"Crawling {Type} Submissions...")
    users = []
    submissions, authors = [], []
    for subreddit in subreddits_info:
        submissions_info, users_info, execution_time = redditCrawler.crawlSubmissions(
            subreddit['display_name'], Type=Type, submission_limit=submission_limit)
        execution_time_data["submissions"] += execution_time[0]
        execution_time_data["__total__submissions"][subreddit['id']
                                                    ] = execution_time[1]
        submissions += submissions_info
        authors += users_info

        print(
            F"Subreddit: {subreddit['display_name']}, crawled {len(submissions_info)} submissions and {len(users_info)} authors.")
    users += authors
    print(
        F"Total: crawled {len(submissions)} submissions and {len(authors)} authors.")

    MongoDBConnector.writeToDB(
        database_name=F"{Type}_Submissions_DB", collection_name=str(date.today()), data=submissions)

    comments, commenters = [], []
    for submission in submissions:
        comments_info, users_info, execution_time = redditCrawler.crawlComments(
            submission_id=submission['id'])
        comments += comments_info
        commenters += users_info
        execution_time_data["comments"] += execution_time[0]
        execution_time_data["__total__comments"][submission['id']
                                                 ] = execution_time[1]
        print(
            F"submission-ID: {submission['id']}, crawled {len(comments_info)} comments and {len(users_info)} commenters.")
    users += commenters
    print(
        F"Total: crawled {len(comments)} comments and {len(commenters)} commenters.")

    MongoDBConnector.writeToDB(
        database_name=F"{Type}_Comments_DB", collection_name=str(date.today()), data=comments)

    MongoDBConnector.writeToDB(
        database_name=F"{Type}_Users_DB", collection_name=str(date.today()), data=users)

execution_time_data['end_time'] = redditCrawler.getTimeStamp()
execution_time_data['id'] = F"{execution_time_data['start_time']}_{redditCrawler.getTimeStamp()}"

# MongoDBConnector.writeToDB(
#    database_name="admin", collection_name=str(date.today()), data=[execution_time_data])

register.set_crawling_start(timer.toc())
