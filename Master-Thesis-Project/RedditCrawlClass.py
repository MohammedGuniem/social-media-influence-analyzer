import praw

class RedditCrawler:

  def __init__(self, client_id, client_secret, user_agent, username, password):
    self.redditCrawler = praw.Reddit(client_id=client_id,
                          client_secret=client_secret,
                          user_agent=user_agent,
                          username=username,
                          password=password)

  def crawlSubreddits(self, Type, limit):
    if Type == "Popular":
      subreddits = self.redditCrawler.subreddits.popular(limit=limit)

      extracted_subreddits = []
      extracted_users = []

      for subreddit in subreddits:
        subreddit_displayname = subreddit.display_name

        moderators = []
        for moderator in self.redditCrawler.subreddit(subreddit_displayname).moderator():
          if not hasattr(moderator, 'id') or not hasattr(moderator, 'name'):
            continue
          user = self.crawlUser(moderator.name)
          if user == "Redditor has no attribute id and/or name":
            continue

          moderator = {
              "id": moderator.id,
              "name": moderator.name,
              "permissions": moderator.mod_permissions
          }
          moderators.append(moderator["name"])

          
          if user not in extracted_users:
            extracted_users.append(user)

        extracted_subreddits.append({
            "display_name": subreddit_displayname,
            "id": subreddit.id,
            "created_utc": subreddit.created_utc,
            "description": subreddit.description,
            "public_description": subreddit.public_description,
            "name": subreddit.name,
            "subscribers": subreddit.subscribers,
            "moderators": moderators,
        })

      return extracted_subreddits, extracted_users

    else:
      return [], []

  def crawlSubmissions(self, subreddit_display_name, limit):
    subreddit = self.redditCrawler.subreddit(subreddit_display_name)
    top = subreddit.new(limit=limit)

    extracted_submissions = []
    extracted_users = []
    extracted_flairs = []

    for submission in top:

      if not hasattr(submission.author, 'id') or not hasattr(submission.author, 'name'):
        continue
      
      flair = None
      if hasattr(submission, 'link_flair_template_id') and hasattr(submission, 'link_flair_text'):
        flair = {
          "link_flair_template_id": submission.link_flair_template_id,
          "link_flair_text": submission.link_flair_text
        }
        if flair not in extracted_flairs:
          extracted_flairs.append(flair) 

      user = self.crawlUser(submission.author.name)
      
      extracted_submissions.append({
        "id": submission.id,
        "author_id": user["id"],
        "author_name": user["name"],
        "created_utc": submission.created_utc,
        "name": submission.name,
        "num_comments": submission.num_comments,
        "upvotes": submission.score,
        "upvote_ratio": submission.upvote_ratio,
        "subreddit_ID": submission.subreddit.id,
        "title": submission.title,
        "url": submission.url,
        "flair": flair
      })

      if user not in extracted_users:
        extracted_users.append(user)

    return extracted_submissions, extracted_users, extracted_flairs

  def crawlComments(self, submission_ID):
    submission = self.redditCrawler.submission(id=submission_ID)
    comments = submission.comments

    extracted_comments = []
    extracted_users = []

    submission.comments.replace_more(limit=None)
    for comment in submission.comments.list():

      if not hasattr(comment.author, 'id') or not hasattr(comment.author, 'name'):
        continue
      
      user = self.crawlUser(comment.author.name)
        
      extracted_comments.append({
        "id": comment.id,
        "subreddit_id": comment.subreddit_id,
        "submission_ID": comment.link_id,
        "parent_ID": comment.parent_id,
        "author_name": user["name"],
        "author_id": user["id"],
        "comment_body": comment.body,
        "created_utc": comment.created_utc,
        "is_submitter": comment.is_submitter,
        "upvotes": comment.score,
      })

      if user not in extracted_users:
        extracted_users.append(user)

    return extracted_comments, extracted_users

  def crawlUser(self, Redditor_name):
    redditor = self.redditCrawler.redditor(name=Redditor_name)

    if hasattr(redditor, 'id') and hasattr(redditor, 'name'):
      extracted_user = {
        "id": redditor.id,
        "name": redditor.name,
        "created_utc": redditor.created_utc,
        "has_verified_email": redditor.has_verified_email,
        "icon_img": redditor.icon_img,
        "is_employee": redditor.is_employee,
        "is_gold": redditor.is_gold,
        "is_suspended": redditor.is_suspended if hasattr(redditor, 'is_suspended') else False,
        "subreddit": redditor.subreddit,
      }
      return extracted_user
    else:
      return "Redditor has no attribute id and/or name"
