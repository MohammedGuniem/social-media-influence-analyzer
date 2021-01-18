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

redditor_name = "vgw8"

redditor = reddit.redditor(name=redditor_name)

if hasattr(redditor, 'id'):

    extracted_redditor = {
        "created_utc": redditor.created_utc,
        "has_verified_email": redditor.has_verified_email,
        "icon_img": redditor.icon_img,
        "id": redditor.id,
        "is_employee": redditor.is_employee,
        "is_gold": redditor.is_gold,
        "is_suspended": redditor.is_suspended if hasattr(redditor, 'is_suspended') else False,
        "name": redditor.name,
        "subreddit": redditor.subreddit,
    }
    print(extracted_redditor)
else:
    print("Redditor has no attribute id")

with open('data/redditor.json', 'w') as outfile:
    json.dump(extracted_redditor, outfile)
