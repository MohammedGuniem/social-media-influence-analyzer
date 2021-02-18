from classes.statistics.CrawlingRegister import CrawlingRegister
from classes.statistics.RunningTime import Timer
from datetime import date
from pathlib import Path
import praw
import json


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

        self.register = CrawlingRegister()
        self.timer = Timer()

        self.register.set_crawling_start(
            crawling_start_time=self.timer.getCurrentTime()
        )

    def getModel(self, path):
        with open(path, 'r') as model_file:
            self.model = json.load(model_file)
            return self.model

    # Method to fetch the top (subreddit_limit?) popular subreddits
    def crawlPopularSubreddits(self, subreddit_limit):
        all_subreddits_crawling_start = self.timer.getCurrentTime()

        subreddits = self.redditCrawler.subreddits.popular(
            limit=subreddit_limit)

        all_subreddits = []
        for subreddit in subreddits:
            subreddit_crawling_start = self.timer.getCurrentTime()
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
                self.timer.getCurrentTime())
            all_subreddits.append(extracted_subreddit)

            subreddit_crawling_runtime = self.timer.calculate_time_difference(
                subreddit_crawling_start)

            self.register.set_subreddit_runtime(
                subreddit_id=subreddit.__getattribute__("id"),
                runtime=subreddit_crawling_runtime
            )

        all_subreddits_crawling_runtime = self.timer.calculate_time_difference(
            last_time_checkpoint=all_subreddits_crawling_start
        )

        self.register.set_subreddits_total_runtime(
            all_subreddits_crawling_runtime
        )

        self.register.set_subreddits_num(
            number_of_crawled_subreddits=len(all_subreddits)
        )

        return all_subreddits

    # Method to crawl submissions from a certain subreddit
    def crawlSubmissions(self, subreddits, submissions_type, submission_limit):

        all_submissions_crawling_start = self.timer.getCurrentTime()
        self.register.add_submissions_type(submissions_type=submissions_type)

        all_submissions = []
        all_users = []

        for subreddit in subreddits:

            extracted_submissions = []
            extracted_users = []

            subreddit_display_name = subreddit['display_name']
            subreddit = self.redditCrawler.subreddit(subreddit_display_name)
            if submissions_type == "New":
                submissions = subreddit.new(limit=submission_limit)
            elif submissions_type == "Hot":
                submissions = subreddit.hot(limit=submission_limit)
            elif submissions_type == "Top":
                submissions = subreddit.top(limit=submission_limit)
            elif submissions_type == "Rising":
                submissions = subreddit.rising(limit=submission_limit)
            else:
                print(
                    "You need to specify one of these 4 valid submission types ['New', 'Hot', 'Top', 'Rising']")
                return "Error"

            for submission in submissions:
                submission_crawling_start = self.timer.getCurrentTime()

                submission_attributes = dir(submission)
                extracted_submission = {}

                if not hasattr(submission, 'author') or not hasattr(submission.author, 'id') or not hasattr(submission.author, 'name'):
                    continue
                extracted_users.append(self.crawlUser(
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
                    self.timer.getCurrentTime()
                )
                extracted_submissions.append(extracted_submission)

                submission_crawling_runtime = self.timer.calculate_time_difference(
                    submission_crawling_start)

                self.register.set_submission_runtime(
                    submission_id=submission.__getattribute__("id"),
                    submissions_type=submissions_type,
                    runtime=submission_crawling_runtime
                )

            all_submissions += extracted_submissions
            all_users += extracted_users

            print(
                F"Subreddit: {subreddit_display_name}, crawled {len(extracted_submissions)} submissions and {len(extracted_users)} authors.")

        self.register.update_users_num(
            number_of_crawled_users=len(all_users),
            submissions_type=submissions_type
        )

        all_submissions_crawling_runtime = self.timer.calculate_time_difference(
            last_time_checkpoint=all_submissions_crawling_start
        )

        self.register.set_submissions_total_runtime(
            runtime=all_submissions_crawling_runtime,
            submissions_type=submissions_type
        )

        self.register.set_submissions_num(
            number_of_crawled_submissions=len(all_submissions),
            submissions_type=submissions_type
        )

        print(
            F"Total: crawled {len(all_submissions)} submissions and {len(all_users)} authors.")

        return all_submissions, all_users

    # Method to crawl comments from a certain submission
    def crawlComments(self, submissions, submissions_type):
        all_comments_crawling_start = self.timer.getCurrentTime()

        all_comments = []
        all_users = []

        for submission in submissions:
            submission = self.redditCrawler.submission(id=submission['id'])

            extracted_comments = []
            extracted_users = []

            comments = submission.comments
            submission.comments.replace_more(limit=3)
            for comment in submission.comments.list():
                comment_crawling_start = self.timer.getCurrentTime()

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
                            self.timer.getCurrentTime()
                        )
                        extracted_comment[local_key] = extracted_value
                    else:
                        continue
                extracted_comments.append(extracted_comment)
                user_info = self.crawlUser(
                    redditor_name=extracted_comment['author_name'])
                extracted_users.append(user_info)

                comment_crawling_runtime = self.timer.calculate_time_difference(
                    comment_crawling_start
                )

                self.register.set_comment_runtime(
                    submissions_type=submissions_type,
                    comment_id=comment.__getattribute__("id"),
                    runtime=comment_crawling_runtime
                )

            all_comments += extracted_comments
            all_users += extracted_users
            print(
                F"submission-ID: {submission.id}, crawled {len(extracted_comments)} comments and {len(extracted_users)} commenters.")

        self.register.update_users_num(
            number_of_crawled_users=len(all_users),
            submissions_type=submissions_type
        )

        all_comments_crawling_runtime = self.timer.calculate_time_difference(
            last_time_checkpoint=all_comments_crawling_start
        )

        self.register.set_comments_total_runtime(
            all_comments_crawling_runtime,
            submissions_type=submissions_type
        )

        self.register.set_comments_num(
            number_of_crawled_comments=len(all_comments),
            submissions_type=submissions_type
        )

        print(
            F"Total: crawled {len(all_comments)} comments and {len(all_users)} commenters.")

        return all_comments, all_users

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
                self.timer.getCurrentTime()
            )
            return extracted_user
        else:
            return "Redditor has no attribute id and/or name"

    def get_running_times(self):
        self.register.set_crawling_end(
            crawling_end_time=self.timer.getCurrentTime()
        )
        return self.register.get_running_times()
