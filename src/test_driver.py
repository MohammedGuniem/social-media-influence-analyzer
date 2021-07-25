from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from classes.modelling.ActivityGraphModelling import ActivityGraph
from classes.crawling.test.TestCrawlClass import TestCrawler
from classes.modelling.UserGraphModelling import UserGraph
from classes.caching.CacheHandler import CacheHandler
from classes.statistics.Statistics import Statistics
from classes.logging.LoggHandler import LoggHandler
from dotenv import load_dotenv
from datetime import date
import os

try:
    today_date = date.today()
    str_date = str(today_date)

    exec_plan = {
        "run_1": {
            "network_name": "Test",
            "submissions_type": "New",
            "stages": ["crawling", "users_modelling", "activities_modelling", "statistics"]
        }
    }

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

        collection_name = str_date

        load_dotenv()

        print(F"Date: {str_date}, Run ID: {run_id}\n")

        # Mongo db database connector
        mongo_db_connector = MongoDBConnector(
            host=get_host('mongo_db_host'),
            port=int(os.environ.get('mongo_db_port')),
            user=os.environ.get('mongo_db_user'),
            passowrd=os.environ.get('mongo_db_pass')
        )

        # Neo4j users database connector
        neo4j_db_users_connector = GraphDBConnector(
            host=get_host('neo4j_users_db_host'),
            port=int(os.environ.get('neo4j_users_db_port')),
            user=os.environ.get('neo4j_users_db_user'),
            password=os.environ.get('neo4j_users_db_pass'),
        )

        # Neo4j activities database connector
        neo4j_db_activities_connector = GraphDBConnector(
            host=get_host('neo4j_activities_db_host'),
            port=int(os.environ.get('neo4j_activities_db_port')),
            user=os.environ.get('neo4j_activities_db_user'),
            password=os.environ.get('neo4j_activities_db_pass'),
        )

        print("Stage 1 - Crawling data...")
        if "crawling" in stages:
            print(
                F"Crawling {network_name} extracting {submissions_type} submissions")

            # Path Where test data is to be found relative to this script
            test_data_path = "classes/crawling/test/TEST_DATA"

            # Test crawler
            crawler = TestCrawler(test_data_path)

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

            # Remove old training set for topic classisification
            mongo_db_connector.remove_collection(
                database_name=F"{network_name}_{submissions_type}_Training_Data",
                collection_name=collection_name
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
            user_model = UserGraph(
                mongo_db_connector=mongo_db_connector,
                neo4j_db_connector=neo4j_db_users_connector,
                network_name=network_name,
                submissions_type=submissions_type,
                date=str_date
            )

            user_model.build()

            user_model.save(graph_type="user_graph")

            print(
                F"User Graph: #nodes: {len(user_model.nodes)}, #edges: {len(user_model.edges)}")
        else:
            print("Jumped over stage 2 as it is not in the stage configuration array.")

        print("\nStage 3 - Building Activities Influence model...")
        if "activities_modelling" in stages:
            activity_model = ActivityGraph(
                mongo_db_connector=mongo_db_connector,
                neo4j_db_connector=neo4j_db_activities_connector,
                network_name=network_name,
                submissions_type=submissions_type,
                date=str_date
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
                str_date
            )

            stat.getCrawlingRuntimes()

            stat.getInfluenceArea()

            for score_type in ["interaction", "activity", "upvotes", "interaction_and_activity", "activity_and_upvotes", "interaction_and_upvotes", "total"]:
                stat.getInfluenceScore(score_type=score_type)

            stat.getInfluenceScore(score_type="single_scores")

            stat.getInfluenceScore(score_type="dobble_scores")

            stat.getInfluenceScore(score_type=None)

            stat.getNodeCentrality()

        else:
            print("Jumped over stage 4 as it is not in the stage configuration array.")

        IS_CACHE_ON = os.environ.get('CACHE_ON')
        if IS_CACHE_ON == "True":
            print("\nRefreshing system cache records...")
            cache_handler = CacheHandler(
                domain_name=os.environ.get('DOMAIN_NAME'),
                cache_directory_path=os.environ.get('CACHE_DIR_PATH'),
                network_name=network_name,
                submissions_type=submissions_type,
                crawling_date=str_date,
                output_msg=False  # set to True to get better debugging and information messages
            )
            cache_handler.refresh_system_cache()
            print("Cache successfully refreshed.")
        else:
            print("\nCaching not enabled")

except Exception as e:
    logg_handler = LoggHandler(str_date)
    logg_handler.logg_driver_error(e, network_name, submissions_type)
