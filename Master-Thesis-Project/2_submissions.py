import praw
import json
import os
import pprint
from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(client_id=os.environ.get('reddit_client_id'),
                     client_secret=os.environ.get('reddit_client_secret'),
                     user_agent=os.environ.get('reddit_user_agent'),
                     username=os.environ.get('reddit_username'),
                     password=os.environ.get('reddit_password'))

subreddit_name = "aviation"
subreddit = reddit.subreddit(subreddit_name)
top = subreddit.new(limit=3)
counter = 1
extracted_submissions = {}
for submission in top:
    submission_ID = submission.id
    submission_author = submission.author.id

    extracted_submissions[submission_ID] = {
        "author": submission_author,
        "created_utc": submission.created_utc,
        "name": submission.name,
        "num_comments": submission.num_comments,
        "upvotes": submission.score,
        "upvote_ratio": submission.upvote_ratio,
        "subreddit_ID": submission.subreddit.id,
        "title": submission.title,
        "url": submission.url,
    }

    counter += 1

with open('data/submissions.json', 'w') as outfile:
    json.dump(extracted_submissions, outfile)
