from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.statistics.CrawlingStatistics import RedditCrawlingStatistics
import os

# Database connection string
MongoDB_connection_string = os.environ.get('mongo_connnection_string')

# Database connector instance.
MongoDBConnector = MongoDBConnector(
    MongoDB_connection_string)

statistics_instance = RedditCrawlingStatistics(MongoDBConnector)

print(F"Crawling Runtime for crawling each reddit object/segment")
crawling_runtime_df = statistics_instance.getCrawlingRunningTime()
print(crawling_runtime_df, "\n")

for submission_type in ["New", "Rising"]:

    print(F"Viweing statistics for {submission_type} submissions:", "\n")

    print("Summary Statistics:")
    targets = ["num_comments", "upvotes", "upvote_ratio", "created_utc"]
    write_to_path = F"Data/{submission_type}_summary_statistics"
    summary_statistics = statistics_instance.getSummaryStatistics(
        submission_type=submission_type,
        targets=targets,
        write_to_path=write_to_path
    )
    print(summary_statistics, "\n")

    print("Difference between oldest and newest submission is:")
    submission_time_interval = statistics_instance.getSubmissionsTimeInterval(
        summary_statistics
    )
    print(submission_time_interval, "\n")

    submissions_per_day = statistics_instance.getPublishedSubmissionsPerDay(
        submission_type=submission_type,
        plot=True,
        save_to=F"Data/{submission_type}_submissions_per_day")

    for day, number_of_submissions in submissions_per_day.items():
        print(F"{day}: {number_of_submissions}")
