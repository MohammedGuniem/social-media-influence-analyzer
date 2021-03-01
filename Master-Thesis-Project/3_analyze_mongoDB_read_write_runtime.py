from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.statistics.Statistics import Statistics as statistics_methods
import os

connection_string = os.environ.get('mongo_connnection_string')

mongo_db_connector = MongoDBConnector(connection_string)


def analyze_runtimes(operations):
    if operations == "write":
        analysis_data = mongo_db_connector.get_writing_runtimes()
        if len(analysis_data) == 0:
            return "Not enough data about read operations"
    elif operations == "read":
        analysis_data = mongo_db_connector.get_reading_runtimes()
        if len(analysis_data) == 0:
            return "Not enough data about read operations"
    else:
        return "You need to specify either read or write as operations type"

    runtimes = {}
    for data in analysis_data:
        data.pop("_id")
        data.pop("created")
        for database, value in data.items():
            if database not in runtimes:
                runtimes[database] = [value]
            else:
                runtimes[database] += [value]

    summary_statistics = statistics_methods.getSummaryStatistics(runtimes)
    return summary_statistics


print("\n Summary Statistics of measured writing runtimes to mongo_db databases")
writing_analysis = analyze_runtimes(operations="write")
print(writing_analysis)

print("\n Summary Statistics of measured reading runtimes to mongo_db databases")
reading_analysis = analyze_runtimes(operations="read")
print(reading_analysis)
