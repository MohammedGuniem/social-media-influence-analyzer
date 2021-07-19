import requests
import shutil
import os


class CacheHandler:

    def __init__(self, domain_name, cache_directory_path, neo4j_db_users_connector, neo4j_db_activities_connector):
        # create cache directory if not found
        if not os.path.exists(cache_directory_path):
            os.makedirs(cache_directory_path)

        self.domain_name = domain_name
        self.cache_directory_path = cache_directory_path
        self.neo4j_db_users_connector = neo4j_db_users_connector
        self.neo4j_db_activities_connector = neo4j_db_activities_connector

        # All possible score types with their combinations
        self.score_types = ["total", "activity", "interaction", "upvotes",
                            "activity_and_upvotes", "interaction_and_activity", "interaction_and_upvotes"]

        # All possible centrality measures
        self.centrality_measures = ["degree_centrality", "betweenness_centrality",
                                    "hits_centrality_hub", "hits_centrality_auth"]

    def check_response(self, url, response, output_msg=False):
        if response.status_code == 200:
            if output_msg:
                print(F"request to {url} - Successed")
            return True
        else:
            if output_msg:
                print(F"request to {url} - Failed")
            return False

    def clear_cache(self, output_msg=False):
        if output_msg:
            print("\n--> Clearing all cache records...")

        if os.path.exists(self.cache_directory_path):
            # shutil.rmtree(self.cache_directory_path)
            # os.mkdir(self.cache_directory_path)
            for cache_record in os.listdir(self.cache_directory_path):
                os.remove(os.path.join(
                    self.cache_directory_path, cache_record))
            if output_msg:
                print("--> All cache records cleared successfully")
        else:
            if output_msg:
                print("--> No cache records to clear")

    def fetchIndexPage(self, output_msg=False):
        if output_msg:
            print("\n--> Refreshing cache for index page...")

        url = F"{self.domain_name}/"
        response = requests.get(url, timeout=54000)
        self.check_response(url, response)

    def fetchUserGraphs(self, output_msg=False):
        if output_msg:
            print("\n--> Refreshing cache for all registered user influence graphs...")

        user_influence_graphs = self.neo4j_db_users_connector.get_graphs()
        for graph in user_influence_graphs:
            for score_type in self.score_types:
                for centrality_measure in self.centrality_measures:
                    url = F"{self.domain_name}/influence_graph?network_name={graph['network']}&submissions_type={graph['submissions_type']}&crawling_date={graph['date']}&score_type={score_type}&centrality={centrality_measure}"
                    response = requests.get(url, timeout=54000)
                    self.check_response(url, response)

    def fetchActivityGraphs(self, output_msg=False):
        if output_msg:
            print("\n--> Refreshing cache for all registered activity graphs...")

        activity_graphs = self.neo4j_db_activities_connector.get_graphs()
        for graph in activity_graphs:
            for score_type in self.score_types:
                url = F"{self.domain_name}/activity_graph?network_name={graph['network']}&submissions_type={graph['submissions_type']}&crawling_date={graph['date']}&score_type={score_type}"
                response = requests.get(url, timeout=54000)
                self.check_response(url, response)

    def fetchCentralityReports(self, output_msg=False):
        if output_msg:
            print(
                "\n--> Refreshing cache for centrality reports of all registered user influence graphs...")

        user_influence_graphs = self.neo4j_db_users_connector.get_graphs()
        for graph in user_influence_graphs:
            url = F"{self.domain_name}/centrality_report?network_name={graph['network']}&submissions_type={graph['submissions_type']}&crawling_date={graph['date']}"
            response = requests.get(url, timeout=54000)
            self.check_response(url, response)

    def fetchTopicDetectionModel(self, output_msg=False):
        if output_msg:
            print("\n--> Refreshing cache for text classifier evaluation and tuning results of all registered user influence graphs...")

        user_influence_graphs = self.neo4j_db_users_connector.get_graphs()
        for graph in user_influence_graphs:
            url = F"{self.domain_name}/topic_detection_model?network_name={graph['network']}&submissions_type={graph['submissions_type']}&crawling_date={graph['date']}"
            response = requests.get(url, timeout=54000)
            self.check_response(url, response)

    def refresh_system_cache(self, output_msg):
        self.clear_cache(output_msg)
        self.fetchIndexPage(output_msg)
        self.fetchUserGraphs(output_msg)
        self.fetchActivityGraphs(output_msg)
        self.fetchCentralityReports(output_msg)
        self.fetchTopicDetectionModel(output_msg)
