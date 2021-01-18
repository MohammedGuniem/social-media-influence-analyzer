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

popular = reddit.subreddits.popular(limit=3)
counter = 1
extracted_subreddits = {}
for subreddit in popular:
    subreddit_name = subreddit.display_name
    subreddit_ID = subreddit.id

    extracted_subreddits[subreddit_ID] = {
        "created_utc": subreddit.created_utc,
        "description": subreddit.description,
        "public_description": subreddit.public_description,
        "fullname": subreddit.name,
        "display_name": subreddit.display_name,
        "subscribers": subreddit.subscribers,
        "moderator": []
    }

    for moderator in reddit.subreddit(subreddit_name).moderator():
        extracted_subreddits[subreddit_ID]["moderator"].append({
            "moderator": moderator.name,
            "permissions": moderator.mod_permissions
        })

    counter += 1

with open('data/subreddits.json', 'w') as outfile:
    json.dump(extracted_subreddits, outfile)
