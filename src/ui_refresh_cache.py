from classes.database_connectors.Neo4jConnector import GraphDBConnector
from classes.caching.CacheHandler import CacheHandler
from dotenv import load_dotenv
import os

load_dotenv()

try:
    domain_name = "http://localhost:5000"
    cache_directory_path = "cache"

    def get_host(target):
        """ Gets the hostname based on the configured environment. """
        if os.environ.get('IS_DOCKER') == "True":
            return "host.docker.internal"
        return os.environ.get(target)

    # Neo4j users database connector
    neo4j_users_db_connector = GraphDBConnector(
        host=get_host('neo4j_users_db_host'),
        port=int(os.environ.get('neo4j_users_db_port')),
        user=os.environ.get('neo4j_users_db_user'),
        password=os.environ.get('neo4j_users_db_pass')
    )

    # Neo4j activity database connector
    neo4j_activities_db_connector = GraphDBConnector(
        host=get_host('neo4j_activities_db_host'),
        port=int(os.environ.get('neo4j_activities_db_port')),
        user=os.environ.get('neo4j_activities_db_user'),
        password=os.environ.get('neo4j_activities_db_pass')
    )

    cache_handler = CacheHandler(domain_name, cache_directory_path,
                                 neo4j_users_db_connector, neo4j_activities_db_connector)

    cache_handler.clear_cache()

    cache_handler.fetchIndexPage()

    cache_handler.fetchUserGraphs()

    cache_handler.fetchActivityGraphs()

    cache_handler.fetchCentralityReports()

    cache_handler.fetchTopicDetectionModel()

except Exception as e:
    print("failed")
    print(e)
