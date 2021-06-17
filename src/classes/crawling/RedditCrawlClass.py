from classes.crawling.CrawlingRuntimeRegister import RuntimeRegister
import time
import praw


class RedditCrawler:

    def __init__(self, client_id, client_secret, user_agent, username, password):
        self.redditCrawler = praw.Reddit(client_id=client_id,
                                         client_secret=client_secret,
                                         user_agent=user_agent,
                                         username=username,
                                         password=password)

        self.runtime_register = RuntimeRegister("Reddit")

    # Method to fetch the top (subreddit_limit?) popular subreddits
    def getGroups(self, top_n_subreddits):
        start = time.time()

        subreddits = self.redditCrawler.subreddits.popular(
            limit=top_n_subreddits)

        all_subreddits = []
        for subreddit in subreddits:
            extracted_subreddit = {
                "id": subreddit.id,
                "display_name": subreddit.display_name
            }
            all_subreddits.append(extracted_subreddit)

        self.runtime_register.groups_count = len(all_subreddits)
        self.runtime_register.groups_crawling_time = time.time() - start

        return all_subreddits

    # Method to crawl submissions from a certain subreddit
    def getSubmissions(self, subreddits, submissions_type, submission_limit):
        start = time.time()

        all_submissions = []

        for subreddit in subreddits:

            extracted_submissions = []

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
                if not hasattr(submission, 'author') or not hasattr(submission.author, 'id') or not hasattr(submission.author, 'name'):
                    continue

                extracted_submission = {
                    "id": submission.id,
                    "author_id": submission.author.id,
                    "author_name": submission.author.name,
                    "num_comments": submission.num_comments,
                    "group_id": submission.subreddit.id,
                    "body": submission.title,
                    "upvotes": submission.score
                }

                extracted_submissions.append(extracted_submission)

            all_submissions += extracted_submissions

            print(
                F"Subreddit: {subreddit_display_name}, crawled {len(extracted_submissions)} submissions.")

        print(
            F"Total: crawled {len(all_submissions)} submissions.")

        self.runtime_register.submissions_type = submissions_type
        self.runtime_register.submissions_count = len(all_submissions)
        self.runtime_register.submissions_crawling_time = time.time() - start

        return all_submissions

        # Method to crawl submissions from a certain subreddit

    # Method to crawl comments from a certain submission
    def getComments(self, submissions, submissions_type):
        start = time.time()

        all_comments = []

        for submission in submissions:
            submission = self.redditCrawler.submission(id=submission['id'])

            extracted_comments = []

            comments = submission.comments
            submission.comments.replace_more(limit=3)
            for comment in submission.comments.list():

                # This to check if the comment is valid and provides a username and user ID
                # unfortunately this check does not work, if we merge all checks into one using OR operator
                if not hasattr(comment, 'author'):
                    continue
                elif not hasattr(comment.author, 'id'):
                    continue
                elif not hasattr(comment.author, 'name'):
                    continue

                extracted_comment = {
                    "id": comment.id,
                    "author_id": comment.author.id,
                    "author_name": comment.author.name,
                    "body": comment.body,
                    "parent_id": comment.parent_id,
                    "submission_id": comment.link_id,
                    "group_id": comment.subreddit_id,
                    "upvotes": comment.score
                }

                extracted_comments.append(extracted_comment)

            all_comments += extracted_comments

            print(
                F"submission-ID: {submission.id}, crawled {len(extracted_comments)} comments.")

        print(
            F"Total: crawled {len(all_comments)} comments.")

        self.runtime_register.comments_count = len(all_comments)
        self.runtime_register.comments_crawling_time = time.time() - start

        return all_comments

    # Method to crawl submissions titles used as training data for Text Classification and Influence area detection
    def getSubmissionsTitles(self, subreddits, submissions_type, submissions_limit):
        all_submissions = []

        for subreddit in subreddits:

            extracted_submissions_titles = []

            subreddit_display_name = subreddit['display_name']
            subreddit = self.redditCrawler.subreddit(subreddit_display_name)
            if submissions_type == "New":
                submissions = subreddit.new(limit=submissions_limit)
            elif submissions_type == "Hot":
                submissions = subreddit.hot(limit=submissions_limit)
            elif submissions_type == "Top":
                submissions = subreddit.top(limit=submissions_limit)
            elif submissions_type == "Rising":
                submissions = subreddit.rising(limit=submissions_limit)
            else:
                print(
                    "You need to specify one of these 4 valid submission types ['New', 'Hot', 'Top', 'Rising']")
                return "Error"

            for submission in submissions:
                if not hasattr(submission, 'title'):
                    continue

                extracted_submissions_titles.append(submission.title)

            all_submissions += extracted_submissions_titles

            print(
                F"Subreddit: {subreddit_display_name}, crawled {len(extracted_submissions_titles)} submissions.")

        print(
            F"Total: crawled {len(all_submissions)} submissions.")

        return all_submissions

    # Method to crawl trainingdata to enable topic classification of a certain submission
    def getInfluenceAreaTrainingData(self, submissions_limit, submissions_type):
        start = time.time()

        topic_subreddits_mapping = {
            "politic": ["politics", "PoliticsPeopleTwitter", "elections"],
            "economy": ["Economics", "economy", "business"],
            "sport": ["sports", "olympics", "worldcup"],
            "entertainment": ["movies", "comedy", "culture"],
            "technology": ["technology", "science", "Futurology"]
        }

        data = {"training_data": []}
        for category, subreddits in topic_subreddits_mapping.items():
            for subreddit in subreddits:
                submissions = self.getSubmissionsTitles(
                    subreddits=[{"display_name": subreddit}], submissions_type=submissions_type, submissions_limit=submissions_limit)
                for submission_title in submissions:
                    data["training_data"].append({
                        "title": submission_title,
                        "label": category
                    })

        self.runtime_register.training_submissions_type = submissions_type
        self.runtime_register.training_submissions_count = len(
            data["training_data"])
        self.runtime_register.training_submissions_crawling_time = time.time() - \
            start

        return data
