from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from classes.modelling.ActivityGraphModelling import ActivityGraph
from classes.modelling.UserGraphModelling import UserGraph
from classes.crawling.RedditCrawlClass import RedditCrawler
from classes.statistics.Statistics import Statistics
from dotenv import load_dotenv
from time import time, ctime
from datetime import date
import logging
import os

try:
    network_name = "Reddit"
    date = str(date.today())

    load_dotenv()

    print("Stage 1 - Crawling data...")

    # Mongo db database connector
    mongo_db_connector = MongoDBConnector(
        host=os.environ.get('mongo_db_host'),
        port=int(os.environ.get('mongo_db_port')),
        user=os.environ.get('mongo_db_user'),
        passowrd=os.environ.get('mongo_db_pass')
    )

    # Reddit crawler
    crawler = RedditCrawler(
        client_id=os.environ.get('reddit_client_id'),
        client_secret=os.environ.get('reddit_client_secret'),
        user_agent=os.environ.get('reddit_user_agent'),
        username=os.environ.get('reddit_username'),
        password=os.environ.get('reddit_password')
    )

    # Name of social network to be crawled
    social_network_name = network_name

    # Setting the submissions type to Rising
    submissions_type = "Rising"

    # Crawling groups
    groups = crawler.getGroups(top_n_subreddits=3)

    # Crawling submissions
    submissions = crawler.getSubmissions(
        subreddits=groups, submission_limit=3, submissions_type=submissions_type)

    # Crawling Comments
    comments = crawler.getComments(submissions, submissions_type)

    # Fetching training submission titles to determine influence area using machine learning
    training_data = crawler.getInfluenceAreaTrainingData(
        submissions_limit=100,
        submissions_type=submissions_type
    )

    collection_name = date

    # Writing groups/subreddits to mongoDB archive
    mongo_db_connector.writeToDB(
        database_name=F"{social_network_name}_Groups_DB",
        collection_name=collection_name,
        data=groups
    )

    # Writing submissions to mongoDB archive
    mongo_db_connector.writeToDB(
        database_name=F"{social_network_name}_{submissions_type}_Submissions_DB",
        collection_name=collection_name,
        data=submissions
    )

    # Writing comments to mongoDB archive
    mongo_db_connector.writeToDB(
        database_name=F"{social_network_name}_{submissions_type}_Comments_DB",
        collection_name=collection_name,
        data=comments
    )

    # Writing training submission titles to determine influence area using machine learning
    mongo_db_connector.writeToDB(database_name=F"{social_network_name}_{submissions_type}_Training_Data",
                                 collection_name=date, data=[training_data])

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

    user_model.build(network_name=network_name, submissions_type="Rising")

    user_model.save(graph_type="user_graph",
                    network_name=network_name, date=date)

    print(
        F"User Graph: #nodes: {len(user_model.nodes)}, #edges: {len(user_model.edges)}")

    # Neo4j activities database connector
    neo4j_db_activities_connector = GraphDBConnector(
        host=os.environ.get('neo4j_activities_db_host'),
        port=int(os.environ.get('neo4j_activities_db_port')),
        user=os.environ.get('neo4j_activities_db_user'),
        password=os.environ.get('neo4j_activities_db_pass'),
    )

    activity_model = ActivityGraph(
        mongo_db_connector=mongo_db_connector,
        neo4j_db_connector=neo4j_db_activities_connector,
        network_name=network_name,
        submissions_type=submissions_type,
        date=date
    )

    activity_model.build(network_name=network_name, submissions_type="Rising")

    activity_model.save(graph_type="activity_graph",
                        network_name=network_name, date=date)

    print(
        F"Activity Graph: #nodes: {len(activity_model.nodes)}, #edges: {len(activity_model.edges)}")

    print("\nStage 3 - Drawing statistics...")

    stat = Statistics(mongo_db_connector, neo4j_db_users_connector)

    stat.getCrawlingRuntimes(network_name=network_name,
                             submissions_type="Rising", from_date=date)

    stat.getInfluenceArea(network_name=network_name,
                          submissions_type="Rising", model_date=date)

    for score_type in ["interaction", "activity", "upvotes", "interaction_and_activity", "activity_and_upvotes", "interaction_and_upvotes", "total"]:
        stat.getInfluenceScore(network_name=network_name,
                               model_date=date, score_type=score_type)

    stat.getInfluenceScore(network_name=network_name,
                           model_date=date, score_type=None)

except Exception as e:
    log_path = F"Logs/{network_name}/{date}/"

    # create logs file if not found
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # create error logger
    logging.basicConfig(filename=F'{log_path}/errors.log', level=logging.INFO)

    # log error
    logging.error(F'\nError: {ctime(time())}\n{str(e)}\n', exc_info=True)
