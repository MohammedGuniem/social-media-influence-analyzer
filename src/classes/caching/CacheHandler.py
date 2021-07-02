import requests
import shutil
import os


class CacheHandler:

    def __init__(self, domain_name, cache_directory_path, neo4j_users_db_connector, neo4j_activities_db_connector):
        self.domain_name = domain_name
        self.cache_directory_path = cache_directory_path
        self.neo4j_users_db_connector = neo4j_users_db_connector
        self.neo4j_activities_db_connector = neo4j_activities_db_connector

        # All possible score types with their combinations
        self.score_types = ["total", "activity", "interaction", "upvotes",
                            "activity_and_upvotes", "interaction_and_activity", "interaction_and_upvotes", "none"]

        # All possible centrality measures
        self.centrality_measures = ["degree_centrality", "betweenness_centrality",
                                    "hits_centrality_hub", "hits_centrality_auth"]

    def check_response(self, url, response):
        if response.status_code == 200:
            print(F"request to {url} - Successed")
        else:
            print(F"request to {url} - Failed")

    def clear_cache(self):
        print("\n--> Clearing all cache records...")

        if os.path.exists(self.cache_directory_path):
            shutil.rmtree(self.cache_directory_path)
            os.mkdir(self.cache_directory_path)
            print("--> All cache records cleared successfully")
        else:
            print("--> No cahce records to clear")

    def fetchIndexPage(self):
        print("\n--> Refreshing cache for index page...")
        url = F"{self.domain_name}/"
        response = requests.get(url, timeout=54000)
        self.check_response(url, response)

    def fetchUserGraphs(self):
        print("\n--> Refreshing cache for all registered user influence graphs...")
        user_influence_graphs = self.neo4j_users_db_connector.get_graphs()
        for graph in user_influence_graphs:
            for score_type in self.score_types:
                for centrality_measure in self.centrality_measures:
                    url = F"{self.domain_name}/user_graph?graph={graph['network']},{graph['submissions_type']},{graph['date']}&score_type={score_type}&centrality={centrality_measure}"
                    response = requests.get(url, timeout=54000)
                    self.check_response(url, response)

    def fetchActivityGraphs(self):
        print("\n--> Refreshing cache for all registered activity graphs...")
        activity_graphs = self.neo4j_activities_db_connector.get_graphs()
        for graph in activity_graphs:
            url = F"/topic_detection_model?graph={graph['network']},{graph['submissions_type']},{graph['date']}"
            for score_type in self.score_types:
                url = F"{self.domain_name}/activity_graph?graph={graph['network']},{graph['submissions_type']},{graph['date']}&score_type={score_type}"
                response = requests.get(url, timeout=54000)
                self.check_response(url, response)

    def fetchCentralityReports(self):
        print("\n--> Refreshing cache for centrality reports of all registered user influence graphs...")
        user_influence_graphs = self.neo4j_users_db_connector.get_graphs()
        for graph in user_influence_graphs:
            url = F"{self.domain_name}/centrality_report?graph={graph['network']},{graph['submissions_type']},{graph['date']}"
            response = requests.get(url, timeout=54000)
            self.check_response(url, response)

    def fetchTopicDetectionModel(self):
        print("\n--> Refreshing cache for text classifier evaluation and tuning results of all registered user influence graphs...")
        user_influence_graphs = self.neo4j_users_db_connector.get_graphs()
        for graph in user_influence_graphs:
            url = F"{self.domain_name}/topic_detection_model?graph={graph['network']},{graph['submissions_type']},{graph['date']}"
            response = requests.get(url, timeout=54000)
            self.check_response(url, response)
