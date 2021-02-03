from datetime import datetime
import praw
import json
from pathlib import Path


class NewRedditCrawler:

    def __init__(self, client_id, client_secret, user_agent, username, password):
        self.redditCrawler = praw.Reddit(client_id=client_id,
                                         client_secret=client_secret,
                                         user_agent=user_agent,
                                         username=username,
                                         password=password)
        self.path = Path(__file__).parent
        with open(F'{self.path}/crawling_models/user.model.json', 'r') as user_model_file:
            self.user_model = json.load(user_model_file)

    # Method to fetch the top (subreddit_limit?) popular subreddits
    def crawlPopularSubreddits(self, subreddit_limit):
        with open(F'{self.path}/crawling_models/subreddit.model.json', 'r') as subreddit_model_file:
            subreddit_model = json.load(subreddit_model_file)

        subreddits = self.redditCrawler.subreddits.popular(
            limit=subreddit_limit)

        subreddits_info = []
        users_info = []

        for subreddit in subreddits:
            subreddit_attributes = dir(subreddit)
            moderators = []
            for moderator in subreddit.moderator():
                if not hasattr(moderator, 'id') or not hasattr(moderator, 'name'):
                    continue

                moderator = {
                    "id": moderator.id,
                    "name": moderator.name,
                    "permissions": moderator.mod_permissions
                }
                moderators.append(moderator)
                users_info.append(self.crawlUser(
                    redditor_name=moderator['name']))
            extracted_subreddit = {}
            for local_key, external_key in subreddit_model.items():
                if external_key == "moderators":
                    extracted_subreddit["moderators"] = moderators
                elif external_key in subreddit_attributes:
                    extracted_subreddit[local_key] = subreddit.__getattribute__(
                        external_key)
            extracted_subreddit["updated_utc"] = round(
                datetime.utcnow().timestamp())
            subreddits_info.append(extracted_subreddit)

        return subreddits_info, users_info

    # Method to crawl submissions from a certain subreddit
    def crawlSubmissions(self, subreddit_display_name, Type, submission_limit):
        with open(F'{self.path}/crawling_models/submission.model.json', 'r') as submission_model_file:
            submission_model = json.load(submission_model_file)

        subreddit = self.redditCrawler.subreddit(subreddit_display_name)
        if Type == "New":
            submissions = subreddit.new(limit=submission_limit)
        elif Type == "Hot":
            submissions = subreddit.hot(limit=submission_limit)
        elif Type == "Top":
            submissions = subreddit.top(limit=submission_limit)
        elif Type == "Rising":
            submissions = subreddit.rising(limit=submission_limit)
        else:
            print(
                "You need to specify one of these 4 valid submission types ['New', 'Hot', 'Top', 'Rising']")
            return "Error"

        submissions_info = []
        users_info = []
        for submission in submissions:
            submission_attributes = dir(submission)
            extracted_submission = {}

            if not hasattr(submission, 'author') or not hasattr(submission.author, 'id') or not hasattr(submission.author, 'name'):
                continue
            users_info.append(self.crawlUser(
                redditor_name=submission.author.name))

            for local_key, external_key in submission_model.items():
                external_sub_keys = external_key.split(".")
                if ("subreddit" in external_sub_keys) and ("id" in external_sub_keys):
                    extracted_value = subreddit.id
                elif ("subreddit" in external_sub_keys) and ("display_name" in external_sub_keys):
                    extracted_value = subreddit_display_name
                elif (len(external_sub_keys) >= 1) and (external_sub_keys[0] in submission_attributes):
                    extracted_value = submission.__getattribute__(
                        external_sub_keys[0])
                    for key in external_sub_keys[1:]:
                        if key in dir(extracted_value):
                            extracted_value = extracted_value.__getattribute__(
                                key)
                    extracted_submission[local_key] = extracted_value
                else:
                    continue

            extracted_submission["updated_utc"] = round(
                datetime.utcnow().timestamp())
            submissions_info.append(extracted_submission)

        return submissions_info, users_info

    # Method to crawl comments from a certain submission
    def crawlComments(self, submission_id):
        with open(F'{self.path}/crawling_models/comment.model.json', 'r') as comment_model_file:
            comment_model = json.load(comment_model_file)

        submission = self.redditCrawler.submission(id=submission_id)

        comments_info = []
        users_info = []

        comments = submission.comments
        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            if not hasattr(comment.author, 'id') or not hasattr(comment.author, 'name'):
                continue

            comment_attributes = dir(comment)
            extracted_comment = {}

            for local_key, external_key in comment_model.items():
                external_sub_keys = external_key.split(".")
                if (len(external_sub_keys) >= 1) and (external_sub_keys[0] in comment_attributes):
                    extracted_value = comment.__getattribute__(
                        external_sub_keys[0])
                    for key in external_sub_keys[1:]:
                        if key in dir(extracted_value):
                            extracted_value = extracted_value.__getattribute__(
                                key)
                    extracted_comment["updated_utc"] = round(
                        datetime.utcnow().timestamp())
                    extracted_comment[local_key] = extracted_value
                else:
                    continue
            comments_info.append(extracted_comment)
            user_info = self.crawlUser(
                redditor_name=extracted_comment['author_name'])
            users_info.append(user_info)

        return comments_info, users_info

    # Method to crawl user meta data
    def crawlUser(self, redditor_name):
        redditor = self.redditCrawler.redditor(name=redditor_name)
        if hasattr(redditor, 'id') and hasattr(redditor, 'name') and not hasattr(redditor, 'is_suspended'):
            extracted_user = {}
            redditor_attributes = dir(redditor)
            for local_key, external_key in self.user_model.items():
                if external_key in redditor_attributes:
                    extracted_user[local_key] = redditor.__getattribute__(
                        external_key)
            extracted_user["updated_utc"] = round(
                datetime.utcnow().timestamp())
            return extracted_user
        else:
            return "Redditor has no attribute id and/or name"
