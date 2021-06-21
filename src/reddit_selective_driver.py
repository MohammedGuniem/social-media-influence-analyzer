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
    exec_plan = {
        "run_1": {
            "network_name": "Selective_Reddit",
            "submissions_type": "New",
            "stages": ["crawling", "users_modelling", "activities_modelling", "statistics"]
        },
        "run_2": {
            "network_name": "Selective_Reddit",
            "submissions_type": "Rising",
            "stages": ["crawling", "users_modelling", "activities_modelling", "statistics"]
        }
    }

    today_date = date.today()

    def get_host(target):
        if os.environ.get('IS_DOCKER') == "True":
            return "host.docker.internal"
        return os.environ.get(target)

    for run_id, config in exec_plan.items():

        # Name of social network to be crawled
        network_name = config["network_name"]

        # Assuming we are crawling the newest submissions
        submissions_type = config["submissions_type"]

        stages = config["stages"]

        date = str(today_date)

        collection_name = date

        load_dotenv()

        print(F"Date: {date}, Run ID: {run_id}\n")

        # Mongo db database connector
        mongo_db_connector = MongoDBConnector(
            host=get_host('mongo_db_host'),
            port=int(os.environ.get('mongo_db_port')),
            user=os.environ.get('mongo_db_user'),
            passowrd=os.environ.get('mongo_db_pass')
        )

        print("Stage 1 - Crawling data...")
        if "crawling" in stages:
            print(
                F"Crawling {network_name} extracting {submissions_type} submissions")

            # Reddit crawler
            crawler = RedditCrawler(
                client_id=os.environ.get('reddit_client_id'),
                client_secret=os.environ.get('reddit_client_secret'),
                user_agent=os.environ.get('reddit_user_agent'),
                username=os.environ.get('reddit_username'),
                password=os.environ.get('reddit_password'),
                network_name=network_name
            )

            # Crawling groups
            groups = [
                {
                    'id': '2qh13',
                    'display_name': 'worldnews'
                }, {
                    'id': '2qhfj',
                    'display_name': 'Finance'
                }, {
                    'id': '2qo4s',
                    'display_name': 'NBA'
                }, {
                    'id': '2r4nf',
                    'display_name': 'Cinema'
                }, {
                    'id': '2qng0',
                    'display_name': 'research'
                }
            ]

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
        else:
            print("Jumped over stage 1 as it is not in the stage configuration array.")

        print("\nStage 2 - Building Users Influence model...")
        if "users_modelling" in stages:
            # Neo4j users database connector
            neo4j_db_users_connector = GraphDBConnector(
                host=get_host('neo4j_users_db_host'),
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
        else:
            print("Jumped over stage 2 as it is not in the stage configuration array.")

        print("\nStage 3 - Building Activities Influence model...")
        if "activities_modelling" in stages:
            # Neo4j activities database connector
            neo4j_db_activities_cconnector = GraphDBConnector(
                host=get_host('neo4j_activities_db_host'),
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
        else:
            print("Jumped over stage 3 as it is not in the stage configuration array.")

        print("\nStage 4 - Drawing statistics...")
        if "statistics" in stages:
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

            stat.getInfluenceScore(score_type="single_scores")

            stat.getInfluenceScore(score_type="dobble_scores")

            stat.getInfluenceScore(score_type=None)
        else:
            print("Jumped over stage 4 as it is not in the stage configuration array.")

except Exception as e:
    log_path = F"Logs/{date}/{network_name}/{submissions_type}/"

    # create logs file if not found
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # create error logger
    logging.basicConfig(filename=F'{log_path}/errors.log', level=logging.INFO)

    # log error
    logging.error(F'\nError: {ctime(time())}\n{str(e)}\n', exc_info=True)
