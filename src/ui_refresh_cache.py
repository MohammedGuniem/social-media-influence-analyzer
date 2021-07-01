from classes.database_connectors.Neo4jConnector import GraphDBConnector
from dotenv import load_dotenv
import requests
import os

load_dotenv()

try:
    domain_name = "http://localhost:5000"

    def get_host(target):
        """ Gets the hostname based on the configured environment. """
        if os.environ.get('IS_DOCKER') == "True":
            return "host.docker.internal"
        return os.environ.get(target)

    def check_response(url, response):
        if response.status_code == 200:
            print(F"request to {url} - Successed")
        else:
            print(F"request to {url} - Failed")

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

    # All possible score types with their combinations
    score_types = ["total", "activity", "interaction", "upvotes",
                   "activity_and_upvotes", "interaction_and_activity", "interaction_and_upvotes", "none"]

    # All possible centrality measures
    centrality_measures = ["degree_centrality", "betweenness_centrality",
                           "hits_centrality_hub", "hits_centrality_auth"]

    print("--> Clearing all cache records...")
    url = F"{domain_name}/clear_cache"
    response = requests.get(url)
    check_response(url, response)

    print("\n--> Refreshing cache for index page...")
    url = F"{domain_name}/"
    response = requests.get(url)
    check_response(url, response)

    user_influence_graphs = neo4j_users_db_connector.get_graphs()

    print("\n--> Refreshing cache for text classifier evaluation and tuning results of all registered user influence graphs...")
    for graph in user_influence_graphs:
        url = F"{domain_name}/topic_detection_model?graph={graph['network']},{graph['submissions_type']},{graph['date']}"
        response = requests.get(url)
        check_response(url, response)

    print("\n--> Refreshing cache for all registered user influence graphs...")
    for graph in user_influence_graphs:
        for score_type in score_types:
            for centrality_measure in centrality_measures:
                url = F"{domain_name}/user_graph?graph={graph['network']},{graph['submissions_type']},{graph['date']}&score_type={score_type}&centrality={centrality_measure}"
                response = requests.get(url)
                check_response(url, response)

    print("\n--> Refreshing cache for centrality reports of all registered user influence graphs...")
    for graph in user_influence_graphs:
        url = F"{domain_name}/centrality_report?graph={graph['network']},{graph['submissions_type']},{graph['date']}"
        response = requests.get(url)
        check_response(url, response)

    print("\n--> Refreshing cache for all registered activity graphs...")
    activity_graphs = neo4j_users_db_connector.get_graphs()
    for graph in activity_graphs:
        url = F"/topic_detection_model?graph={graph['network']},{graph['submissions_type']},{graph['date']}"
        for score_type in score_types:
            url = F"{domain_name}/activity_graph?graph={graph['network']},{graph['submissions_type']},{graph['date']}&score_type={score_type}"
            response = requests.get(url)
            check_response(url, response)

except:
    print("failed")
