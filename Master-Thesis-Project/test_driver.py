from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from classes.modelling.ActivityGraphModelling import ActivityGraph
from classes.modelling.UserGraphModelling import UserGraph
from classes.crawling.RedditCrawlClass import RedditCrawler
from classes.crawling.TestCrawlClass import TestCrawler
from classes.statistics.Statistics import Statistics
from dotenv import load_dotenv
from time import time, ctime
from datetime import date
import logging
import os

try:
    # Name of social network to be crawled
    network_name = "Test"

    # Assuming we are crawling the newest submissions
    submissions_type = "New"

    date = str(date.today())

    collection_name = date

    load_dotenv()

    print("Stage 1 - Crawling data...")

    # Mongo db database connector
    mongo_db_connector = MongoDBConnector(
        host=os.environ.get('mongo_db_host'),
        port=int(os.environ.get('mongo_db_port')),
        user=os.environ.get('mongo_db_user'),
        passowrd=os.environ.get('mongo_db_pass')
    )

    # Test crawler
    crawler = TestCrawler()

    # Crawling groups/subreddits
    groups = crawler.getGroups()

    # Crawling submissions
    submissions = crawler.getSubmissions()

    # Crawling Comments
    comments = crawler.getComments()

    # Fetching training submission titles to determine influence area using machine learning
    training_data = crawler.getInfluenceAreaTrainingData()

    # Writing groups/subreddits to mongoDB archive
    mongo_db_connector.writeToDB(
        database_name=F"{network_name}_{submissions_type}_Groups_DB",
        collection_name=collection_name,
        data=groups
    )

    # Writing submissions to mongoDB archive
    mongo_db_connector.writeToDB(
        database_name=F"{network_name}_{submissions_type}_Submissions_DB",
        collection_name=collection_name,
        data=submissions
    )

    # Writing comments to mongoDB archive
    mongo_db_connector.writeToDB(
        database_name=F"{network_name}_{submissions_type}_Comments_DB",
        collection_name=collection_name,
        data=comments
    )

    # Writing training submission titles to determine influence area using machine learning
    mongo_db_connector.writeToDB(
        database_name=F"{network_name}_{submissions_type}_Training_Data",
        collection_name=collection_name, data=[training_data]
    )

    # Fetching the registered runtimes from this crawling run
    runtime_register = crawler.runtime_register.getRunningTime()

    # logging the runtime register into admin DB in mongoDB
    mongo_db_connector.writeToDB(
        database_name="admin",
        collection_name="crawling_runtime_register",
        data=[runtime_register]
    )

    print("\nStage 2 - Building Influence model...")

    # Neo4j users database connector
    neo4j_db_users_connector = GraphDBConnector(
        host=os.environ.get('neo4j_users_db_host'),
        port=int(os.environ.get('neo4j_users_db_port')),
        user=os.environ.get('neo4j_users_db_user'),
        password=os.environ.get('neo4j_users_db_pass'),
    )

    user_model = UserGraph(
        mongo_db_connector=mongo_db_connector,
        neo4j_db_connector=neo4j_db_users_connector,
        network_name=network_name,
        submissions_type=submissions_type,
        date=date
    )

    user_model.build()

    user_model.save(graph_type="user_graph")

    print(
        F"User Graph: #nodes: {len(user_model.nodes)}, #edges: {len(user_model.edges)}")

    # Neo4j activities database connector
    neo4j_db_activities_cconnector = GraphDBConnector(
        host=os.environ.get('neo4j_activities_db_host'),
        port=int(os.environ.get('neo4j_activities_db_port')),
        user=os.environ.get('neo4j_activities_db_user'),
        password=os.environ.get('neo4j_activities_db_pass'),
    )

    activity_model = ActivityGraph(
        mongo_db_connector=mongo_db_connector,
        neo4j_db_connector=neo4j_db_activities_cconnector,
        network_name=network_name,
        submissions_type=submissions_type,
        date=date
    )

    activity_model.build()

    activity_model.save(graph_type="activity_graph")

    print(
        F"Activity Graph: #nodes: {len(activity_model.nodes)}, #edges: {len(activity_model.edges)}")

    print("\nStage 3 - Drawing statistics...")

    stat = Statistics(
        mongo_db_connector,
        neo4j_db_users_connector,
        network_name,
        submissions_type,
        date
    )

    stat.getCrawlingRuntimes()

    stat.getInfluenceArea()

    for score_type in ["interaction", "activity", "upvotes", "interaction_and_activity", "activity_and_upvotes", "interaction_and_upvotes", "total"]:
        stat.getInfluenceScore(score_type=score_type)

    stat.getInfluenceScore(score_type=None)

except Exception as e:
    log_path = F"Logs/{date}/{network_name}/{submissions_type}/"

    # create logs file if not found
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # create error logger
    logging.basicConfig(filename=F'{log_path}/errors.log', level=logging.INFO)

    # log error
    logging.error(F'\nError: {ctime(time())}\n{str(e)}\n', exc_info=True)
