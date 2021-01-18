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

submission_ID = "kwjns7"
submission_ID = "kz8dr2"
submission = reddit.submission(id=submission_ID)
comments = submission.comments

counter = 0
extracted_comments = {}

submission.comments.replace_more(limit=None)
for comment in submission.comments.list():

    if not hasattr(comment.author, 'id'):
        continue

    extracted_comments[comment.id] = {
        "author": comment.author.id,
        "comment_body": comment.body,
        "created_utc": comment.created_utc,
        "is_submitter": comment.is_submitter,
        "submission_ID": comment.link_id,
        "parent_ID": comment.parent_id,
        "upvotes": comment.score,
        "subreddit_id": comment.subreddit_id
    }
    counter += 1

with open('data/comments.json', 'w') as outfile:
    json.dump(extracted_comments, outfile)
