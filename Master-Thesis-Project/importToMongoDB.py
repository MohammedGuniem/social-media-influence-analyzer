from classes.RedditCrawlClass import RedditCrawler
from classes.MongoDBConnector import MongoDBConnector
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
MongoDB_connection_string = os.environ.get('mongo_connnection_string')


redditCrawler = RedditCrawler(
    client_id, client_secret, user_agent, username, password)

target_subreddits = redditCrawler.getPopularSubreddits(limit=3)

data = {
    "subreddits": [],
    "submissions": [],
    "comments": [],
    "users": []
}

for subreddit_display_name in target_subreddits:
    # Crawl Subreddit
    print(F"STARTED - crawling the '{subreddit_display_name}' subreddit...")
    subreddit_data = redditCrawler.getSubredditData(
        display_name=subreddit_display_name)
    data["subreddits"].append(subreddit_data)
    print(F"DONE")

    # Crawl Submissions from current Subreddit
    print(
        F"STARTED - crawling new submissions from the '{subreddit_display_name}' subreddit...")
    submissions_data = redditCrawler.crawlSubmissions(
        Type="New Submissions", limit=3, subreddit_display_name=subreddit_display_name)
    data["submissions"].append(submissions_data)
    print(F"DONE")

    # Crawl Comments from current Submissions
    print(
        F"STARTED - crawling comments from the new submissions on the '{subreddit_display_name}' subreddit...")
    for submission in submissions_data:
        comments_data = redditCrawler.crawlComments(
            submission_id=submission["id"])
        data["comments"].append(comments_data)
    print(F"DONE")

    # Crawl Users from current Subreddit, Comments, Submissions
    print(
        F"STARTED - crawling users from the '{subreddit_display_name}' subreddit...")

    for moderator in subreddit_data["moderators"]:
        user_data = redditCrawler.crawlUser(
            Redditor_name=moderator["name"])
        if user_data != "Redditor has no attribute id and/or name" and user_data not in data["users"]:
            data["users"].append(user_data)

    for submission in submissions_data:
        user_data = redditCrawler.crawlUser(
            Redditor_name=submission["author_name"])
        if user_data != "Redditor has no attribute id and/or name" and user_data not in data["users"]:
            data["users"].append(user_data)

    for comment in comments_data:
        user_data = redditCrawler.crawlUser(
            Redditor_name=comment["author_name"])
        if user_data != "Redditor has no attribute id and/or name" and user_data not in data["users"]:
            data["users"].append(user_data)

    print(F"DONE")

MongoDBConnector = MongoDBConnector(MongoDB_connection_string)

print(F"Writing Subreddits data to Subreddits_DB")
MongoDBConnector.writeToMongoDB(
    database_name="Subreddits_DB", collection_name=str(date.today()), data=data["subreddits"])
print(F"DONE")

print(F"Writing Submissions data to Submissions_DB")
for submissions_data in data["submissions"]:
    MongoDBConnector.writeToMongoDB(database_name="Submissions_DB",
                                    collection_name=str(date.today()), data=submissions_data)
print(F"DONE")

print(F"Writing Comments data to Comments_DB")
for comments_data in data["comments"]:
    MongoDBConnector.writeToMongoDB(database_name="Comments_DB",
                                    collection_name=str(date.today()), data=comments_data)
print(F"DONE")

print(F"Writing Users data to Users_DB")
MongoDBConnector.writeToMongoDB(database_name="Users_DB",
                                collection_name=str(date.today()), data=data["users"])
print(F"DONE")
