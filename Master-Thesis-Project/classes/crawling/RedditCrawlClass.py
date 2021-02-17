from datetime import datetime
import praw
import json
from pathlib import Path


class RedditCrawler:

    def __init__(self, client_id, client_secret, user_agent, username, password):
        self.redditCrawler = praw.Reddit(client_id=client_id,
                                         client_secret=client_secret,
                                         user_agent=user_agent,
                                         username=username,
                                         password=password)
        path = Path(__file__).parent
        self.subreddit_model = self.getModel(
            F'{path}/crawling_models/subreddit.model.json')
        self.submission_model = self.getModel(
            F'{path}/crawling_models/submission.model.json')
        self.comment_model = self.getModel(
            F'{path}/crawling_models/comment.model.json')
        self.user_model = self.getModel(
            F'{path}/crawling_models/user.model.json')

    def getModel(self, path):
        with open(path, 'r') as model_file:
            self.model = json.load(model_file)
            return self.model

    # Method to fetch the top (subreddit_limit?) popular subreddits
    def crawlPopularSubreddits(self, subreddit_limit):
        method_start = self.getTimeStamp()

        subreddits = self.redditCrawler.subreddits.popular(
            limit=subreddit_limit)

        subreddits_info = []
        running_times = []

        for subreddit in subreddits:
            subreddit_start_reading = self.getTimeStamp()

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

            extracted_subreddit = {}
            for local_key, external_key in self.subreddit_model.items():
                if external_key == "moderators":
                    extracted_subreddit["moderators"] = moderators
                elif external_key in subreddit_attributes:
                    extracted_subreddit[local_key] = subreddit.__getattribute__(
                        external_key)
            extracted_subreddit["updated_utc"] = round(
                datetime.utcnow().timestamp())
            subreddits_info.append(extracted_subreddit)

            subreddit_end_reading = self.getTimeStamp()
            running_times.append({
                'subreddit_id': subreddit.__getattribute__(
                    "id"),
                'subreddit_display_name': subreddit.__getattribute__(
                    "display_name"),
                'start_reading_time': subreddit_start_reading,
                'end_reading_time': subreddit_end_reading,
                'elapsed_time': subreddit_end_reading - subreddit_start_reading
            })
        method_end = self.getTimeStamp()
        total_running_time = {
            'start_reading_time': method_start,
            'end_reading_time': method_end,
            'elapsed_time': method_end - method_start
        }
        execution_time_data = [running_times, total_running_time]
        return subreddits_info, execution_time_data

    # Method to crawl submissions from a certain subreddit
    def crawlSubmissions(self, subreddit_display_name, Type, submission_limit):
        method_start = self.getTimeStamp()

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
        running_times = []

        for submission in submissions:
            submission_start_reading = self.getTimeStamp()

            submission_attributes = dir(submission)
            extracted_submission = {}

            if not hasattr(submission, 'author') or not hasattr(submission.author, 'id') or not hasattr(submission.author, 'name'):
                continue
            users_info.append(self.crawlUser(
                redditor_name=submission.author.name))

            for local_key, external_key in self.submission_model.items():
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
                else:
                    continue
                extracted_submission[local_key] = extracted_value

            extracted_submission["updated_utc"] = round(
                datetime.utcnow().timestamp())
            submissions_info.append(extracted_submission)

            submission_end_reading = self.getTimeStamp()
            running_times.append({
                'submission_id': submission.__getattribute__(
                    "id"),
                'start_reading_time': submission_start_reading,
                'end_reading_time': submission_end_reading,
                'elapsed_time': submission_end_reading - submission_start_reading
            })
        method_end = self.getTimeStamp()
        total_running_time = {
            'start_reading_time': method_start,
            'end_reading_time': method_end,
            'elapsed_time': method_end - method_start
        }
        execution_time_data = [running_times, total_running_time]
        return submissions_info, users_info, execution_time_data

    # Method to crawl comments from a certain submission
    def crawlComments(self, submission_id):
        method_start = self.getTimeStamp()

        submission = self.redditCrawler.submission(id=submission_id)
        comments_info = []
        users_info = []
        running_times = []

        comments = submission.comments
        submission.comments.replace_more(limit=3)
        for comment in submission.comments.list():
            comment_start_reading = self.getTimeStamp()

            if not hasattr(comment.author, 'id') or not hasattr(comment.author, 'name'):
                continue

            comment_attributes = dir(comment)
            extracted_comment = {}

            for local_key, external_key in self.comment_model.items():
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

            comment_end_reading = self.getTimeStamp()
            running_times.append({
                'comment_id': comment.__getattribute__(
                    "id"),
                'start_reading_time': comment_start_reading,
                'end_reading_time': comment_end_reading,
                'elapsed_time': comment_end_reading - comment_start_reading
            })

        method_end = self.getTimeStamp()
        total_running_time = {
            'start_reading_time': method_start,
            'end_reading_time': method_end,
            'elapsed_time': method_end - method_start
        }
        execution_time_data = [running_times, total_running_time]

        return comments_info, users_info, execution_time_data

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
