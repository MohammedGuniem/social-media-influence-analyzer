from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.statistics.Statistics import Statistics as statistics_methods
import os

connection_string = os.environ.get('mongo_connnection_string')

mongo_db_connector = MongoDBConnector(connection_string)

crawling_analysis_data = mongo_db_connector.get_crawling_runtimes()

all_submissions_num = []
all_submissions_crawling_runtime = []
all_comments_num = []
all_comments_crawling_runtime = []

single_submissions_crawling_runtimes = []
single_comments_crawling_runtimes = []

for data in crawling_analysis_data:
    for category, v in data['subreddit_events'].items():
        submissions_num = data['subreddit_events'][category]['submissions_num']
        all_submissions_num.append(submissions_num)

        submissions_total_runtime = data['subreddit_events'][category]['submissions_total_runtime']
        all_submissions_crawling_runtime.append(submissions_total_runtime)

        comments_num = data['subreddit_events'][category]['comments_num']
        all_comments_num.append(comments_num)

        comments_total_runtime = data['subreddit_events'][category]['comments_total_runtime']
        all_comments_crawling_runtime.append(comments_total_runtime)

        single_submissions_crawling_runtimes += data['subreddit_events'][category]['submissions_runtimes'].values()

        single_comments_crawling_runtimes += data['subreddit_events'][category]['comments_runtimes'].values()

""" Plotting runtime versus submissions and comments count """

statistics_methods.plot(
    x=all_submissions_num,
    y=all_submissions_crawling_runtime,
    xlabel="crawling runtime (s)",
    ylabel="number of crawled submissions",
)

statistics_methods.plot(
    x=all_comments_num,
    y=all_comments_crawling_runtime,
    xlabel="crawling runtime (s)",
    ylabel="number of crawled comments",
)

""" Viewing basic statistics about indivdual crawling runtimes for submissions and comments """

submissions_runtime_summary_statistics = statistics_methods.getSummaryStatistics(
    {"submissions crawling runtimes": single_submissions_crawling_runtimes}
)
print(submissions_runtime_summary_statistics)

comments_runtime_summary_statistics = statistics_methods.getSummaryStatistics(
    {"comments crawling runtimes": single_comments_crawling_runtimes}
)
print(comments_runtime_summary_statistics)
