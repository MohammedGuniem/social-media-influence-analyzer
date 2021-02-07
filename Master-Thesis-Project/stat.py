from classes.database_connectors.MongoDBConnector import MongoDBConnector
import pandas as pd
import os
import matplotlib
import matplotlib.pyplot as plt
import datetime

MongoDB_connection_string = os.environ.get('mongo_connnection_string')

# Database connector
MongoDBConnector = MongoDBConnector(
    MongoDB_connection_string)

# For each subreddit:
# 1) get all new submissions, and make pandas dataframe -ok
# 2) calculate basic statistics for: created_utc, num_comments, upvotes, upvote_ratio
#   basic statistics are: count -ok, mean -ok, median -ok, mode -ok, standard diviation -ok, variance -ok, minimum -ok, maximum -ok, percentiles -ok
# 3) calculate the duration of the crawling algorithm. -ok
# 4) plot number of published submissions per day- -ok

target_subreddits = MongoDBConnector.getSubredditsInfo()
submissions = []
for subreddit in target_subreddits:
    print(F"Subreddit: {subreddit['display_name']} {subreddit['id']}")
    submissions += MongoDBConnector.getSubmissionsOnSubreddit(
        subreddit_id=subreddit['id'], Type="New")
print("\n")

submissions_df = pd.DataFrame(submissions)
submissions_df = submissions_df[[
    "id", "author_id", "author_name", "num_comments", "upvotes", "upvote_ratio", "created_utc"]]

targets = ["num_comments", "upvotes", "upvote_ratio", "created_utc"]
targets_df = submissions_df[targets]

print(targets_df.head(10))
print("\n")

summary_statistics = targets_df.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9]).rename(
    index={'50%': '50% - median'})
mode_statistics = targets_df.mode().rename(index={0: 'mode'}).iloc[0]
summary_statistics = summary_statistics.append(mode_statistics)
var_statistics = pd.DataFrame(
    targets_df.var()).transpose().rename(index={0: 'var'})
summary_statistics = summary_statistics.append(var_statistics)
print(summary_statistics)
print("\n")

publish_time_diff = summary_statistics["created_utc"]["max"] - \
    summary_statistics["created_utc"]["min"]
print(F"Difference between oldest and newest submission is:")
print(F"{publish_time_diff} seconds")
print(F"{publish_time_diff/60} minutes")
print(F"{(publish_time_diff/60)/60} hours")
print(F"{((publish_time_diff/60)/60)/24} days")
print(F"{(((publish_time_diff/60)/60)/24)/(365/12)} months")
print(F"{(((publish_time_diff/60)/60)/24)/365} years")
print("\n")

running_time_data = MongoDBConnector.getRunningTime()


def convertSecToHours(seconds):
    return round(((seconds)/60)/60, 2)


total_runtime = convertSecToHours(
    running_time_data[0]["end_time"] - running_time_data[0]["start_time"])

subreddits_runtime = running_time_data[0]["__total__subreddits"]["elapsed_time"]

submissions_runtime = 0
for _, sub in running_time_data[0]["__total__submissions"].items():
    submissions_runtime += sub["elapsed_time"]
submissions_runtime = convertSecToHours(submissions_runtime)

comments_runtime = 0
for _, com in running_time_data[0]["__total__comments"].items():
    comments_runtime += com["elapsed_time"]
comments_runtime = convertSecToHours(comments_runtime)

print(F"Total Crawling Time: {total_runtime} hours")
print(F"Subreddits Info. Crawling Time: {subreddits_runtime} seconds")
print(F"Submissions Info. Crawling Time: {submissions_runtime} hours")
print(F"Comments Info. Crawling Time: {comments_runtime} hours")

submissions_per_day = {}
for sub in submissions:
    created_utc = int(sub['created_utc'])
    timestamp = datetime.datetime.fromtimestamp(created_utc)
    day = timestamp.strftime('%Y-%m-%d')

    if day in submissions_per_day:
        submissions_per_day[day] += 1
    else:
        submissions_per_day[day] = 1

utc_times = sorted(list(submissions_per_day.keys()))
num_submissions = [submissions_per_day[utc_time] for utc_time in utc_times]
fig, ax = plt.subplots()
ax.plot(utc_times, num_submissions, 'o-')
ax.set(xlabel='time in days', ylabel='number of published submissions',
       title='number of published submissions per day')
ax.set_xticklabels(ax.get_xticks(), rotation=45)
ax.grid()
fig.savefig("test.png")
plt.show()
