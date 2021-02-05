from datetime import datetime
import praw


class RedditCrawler:

    def __init__(self, client_id, client_secret, user_agent, username, password):
        self.redditCrawler = praw.Reddit(client_id=client_id,
                                         client_secret=client_secret,
                                         user_agent=user_agent,
                                         username=username,
                                         password=password)

    # Method to fetch the top (limit) popular subreddits
    def getPopularSubreddits(self, limit):
        subreddits = self.redditCrawler.subreddits.popular(limit=limit)
        subreddits_display_names = []
        for subreddit in subreddits:
            subreddits_display_names.append(subreddit.display_name)
        return subreddits_display_names

    # Method to crawl subreddit meta data
    def getSubredditData(self, display_name):

        subreddit = self.redditCrawler.subreddit(display_name)

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

        subreddit_data = {
            "display_name": display_name,
            "id": subreddit.id,
            "created_utc": subreddit.created_utc,
            "updated_utc": round(datetime.utcnow().timestamp()),
            "description": subreddit.description,
            "public_description": subreddit.public_description,
            "name": subreddit.name,
            "count_of_subscribers": subreddit.subscribers,
            "count_of_moderators": len(moderators),
            "moderators": moderators,
        }

        return subreddit_data

    # Method to crawl submissions from a certain subreddit
    def crawlSubmissions(self, Type, limit, subreddit_display_name):
        subreddit = self.redditCrawler.subreddit(subreddit_display_name)

        if Type == "New":
            submissions = subreddit.new(limit=limit)
        elif Type == "Hot":
            submissions = subreddit.hot(limit=limit)
        elif Type == "Top":
            submissions = subreddit.top(limit=limit)
        elif Type == "Rising":
            submissions = subreddit.rising(limit=limit)
        else:
            print("You need to specify a submission type")
            return []

        submissions_data = []

        for submission in submissions:

            if not hasattr(submission, 'author') or not hasattr(submission.author, 'id') or not hasattr(submission.author, 'name'):
                continue

            flair = None
            if hasattr(submission, 'link_flair_template_id') and hasattr(submission, 'link_flair_text'):
                flair = {
                    "link_flair_template_id": submission.link_flair_template_id,
                    "link_flair_text": submission.link_flair_text,
                    "updated_utc": round(datetime.utcnow().timestamp())
                }

            submissions_data.append({
                "id": submission.id,
                "author_id": submission.author.id,
                "author_name": submission.author.name,
                "created_utc": submission.created_utc,
                "updated_utc": round(datetime.utcnow().timestamp()),
                "name": submission.name,
                "num_comments": submission.num_comments,
                "upvotes": submission.score,
                "upvote_ratio": submission.upvote_ratio,
                "subreddit_id": submission.subreddit.id,
                "title": submission.title,
                "url": submission.url,
                "flair": flair
            })

        return submissions_data

    # Method to crawl comments from a certain submission
    def crawlComments(self, submission_id):
        submission = self.redditCrawler.submission(id=submission_id)
        comments = submission.comments

        comments_data = []

        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():

            if not hasattr(comment.author, 'id') or not hasattr(comment.author, 'name'):
                continue

            comments_data.append({
                "id": comment.id,
                "subreddit_id": comment.subreddit_id,
                "submission_id": comment.link_id,
                "parent_id": comment.parent_id,
                "author_id": comment.author.id,
                "author_name": comment.author.name,
                "comment_body": comment.body,
                "created_utc": comment.created_utc,
                "updated_utc": round(datetime.utcnow().timestamp()),
                "is_submitter": comment.is_submitter,
                "upvotes": comment.score,
            })

        return comments_data

    # Method to crawl user meta data
    def crawlUser(self, Redditor_name):
        redditor = self.redditCrawler.redditor(name=Redditor_name)

        if hasattr(redditor, 'id') and hasattr(redditor, 'name'):
            extracted_user = {
                "id": redditor.id,
                "name": redditor.name,
                "created_utc": redditor.created_utc,
                "updated_utc": round(datetime.utcnow().timestamp()),
                "has_verified_email": redditor.has_verified_email,
                "icon_img": redditor.icon_img,
                "is_employee": redditor.is_employee,
                "is_gold": redditor.is_gold,
                "is_suspended": redditor.is_suspended if hasattr(redditor, 'is_suspended') else False
            }
            return extracted_user
        else:
            return "Redditor has no attribute id and/or name"
