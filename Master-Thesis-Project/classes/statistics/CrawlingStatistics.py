import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import numpy as np
import matplotlib
import datetime


class RedditCrawlingStatistics:

    def __init__(self, db_connector):
        self.MongoDBConnector = db_connector

    def getSubmissionsDataframe(self, submission_type):
        # Get info about each crawled subreddit.
        target_subreddits = self.MongoDBConnector.getSubredditsInfo()

        # Gather submissions from each crawled subreddit
        submissions = []
        for subreddit in target_subreddits:
            submissions += self.MongoDBConnector.getSubmissionsOnSubreddit(
                subreddit_id=subreddit['id'], Type=submission_type)

        return submissions

    def getSummaryStatistics(self, submission_type, targets, write_to_path=None):
        # Get submissions from database.
        submissions = self.getSubmissionsDataframe(submission_type)

        # Make pandas dataframe of submissions.
        submissions_df = pd.DataFrame(submissions)

        # Select target columns.
        targets_df = submissions_df[targets]

        # Rename '50%' percentile to '50% - median' since it is the same.
        summary_statistics = targets_df.describe(
            percentiles=[0.1, 0.25, 0.5, 0.75, 0.9]).rename(index={'50%': '50% - median'})

        # Calculate mode and append to statistics dataframe.
        mode_statistics = targets_df.mode().rename(index={0: 'mode'}).iloc[0]
        summary_statistics = summary_statistics.append(mode_statistics)

        # Calculate variance and append to statistics dataframe.
        var_statistics = pd.DataFrame(
            targets_df.var()).transpose().rename(index={0: 'var'})
        summary_statistics = summary_statistics.append(var_statistics)

        if write_to_path:
            summary_statistics.to_csv(
                F'{write_to_path}.csv')

        return summary_statistics

    def getSubmissionsTimeInterval(self, summary_statistics):
        publish_time_diff = summary_statistics["created_utc"]["max"] - \
            summary_statistics["created_utc"]["min"]

        mi = round(publish_time_diff/60, 2)
        h = round((mi)/60, 2)
        d = round((h)/24, 2)
        mo = round((d)/(365/12), 2)
        y = round((d)/(365), 2)

        intervals_df = pd.DataFrame({
            'in seconds': [publish_time_diff],
            'in minutes': [mi],
            'in hours': [h],
            'in days': [d],
            'in months': [mo],
            'in years': [y]
        }, index=['Time difference'])

        return intervals_df

    def convertSecToHours(self, seconds):
        hours = ((seconds)/60)/60
        round_by = 2
        rounded_value = round(hours, round_by)
        while rounded_value == 0:
            round_by += 1
            rounded_value = round(hours, round_by)
        return rounded_value

    def getCrawlingRunningTime(self):
        running_time_data = self.MongoDBConnector.getRunningTime()

        total_runtime = self.convertSecToHours(
            running_time_data[0]["end_time"] - running_time_data[0]["start_time"])

        subreddits_runtime = self.convertSecToHours(
            running_time_data[0]["__total__subreddits"]["elapsed_time"])

        submissions_runtime = 0
        for _, sub in running_time_data[0]["__total__submissions"].items():
            submissions_runtime += sub["elapsed_time"]
        submissions_runtime = self.convertSecToHours(submissions_runtime)

        comments_runtime = 0
        for _, com in running_time_data[0]["__total__comments"].items():
            comments_runtime += com["elapsed_time"]
        comments_runtime = self.convertSecToHours(comments_runtime)

        columns = ('Total Crawling Runtime', 'Crawling Subreddits',
                   'Crawling Submissions', 'Crawling Comments')

        crawling_runtime_df = pd.DataFrame({
            'Total Crawling Runtime': [total_runtime],
            'Crawling Subreddits': [subreddits_runtime],
            'Crawling Submissions': [submissions_runtime],
            'Crawling Comments': [comments_runtime]
        }, index=['Hours'])

        return crawling_runtime_df

    def getPublishedSubmissionsPerDay(self, submission_type, plot=False, save_to=None):
        submissions = self.getSubmissionsDataframe(submission_type)
        submissions_per_day = {}
        for sub in submissions:
            created_utc = int(sub['created_utc'])
            timestamp = datetime.datetime.fromtimestamp(created_utc)
            day = timestamp.strftime('%Y-%m-%d')

            if day in submissions_per_day:
                submissions_per_day[day] += 1
            else:
                submissions_per_day[day] = 1

        if plot:
            utc_times = sorted(list(submissions_per_day.keys()))
            num_submissions = [submissions_per_day[utc_time]
                               for utc_time in utc_times]
            fig, ax = plt.subplots()
            ax.plot(utc_times, num_submissions, 'o-')
            ax.set(xlabel='time in days', ylabel='number of published submissions',
                   title='number of published submissions per day')

            ax.grid()

            if save_to:
                fig.savefig(F"{save_to}.png")

            plt.gcf().autofmt_xdate()
            plt.show()

        return submissions_per_day
