import requests
import hashlib
import os


class CacheHandler:

    def __init__(self, domain_name, cache_directory_path, neo4j_db_users_connector, neo4j_db_activities_connector, network_name, submissions_type, crawling_date, output_msg=False):
        # create cache directory if not found
        if not os.path.exists(cache_directory_path):
            os.makedirs(cache_directory_path)

        self.domain_name = domain_name
        self.cache_directory_path = cache_directory_path
        self.neo4j_db_users_connector = neo4j_db_users_connector
        self.neo4j_db_activities_connector = neo4j_db_activities_connector
        self.network_name = network_name
        self.submissions_type = submissions_type
        self.crawling_date = crawling_date
        self.output_msg = output_msg

        # All possible score types with their combinations
        self.score_types = ["total", "activity", "interaction", "upvotes",
                            "activity_and_upvotes", "interaction_and_activity", "interaction_and_upvotes"]

        # All possible centrality measures
        self.centrality_measures = ["degree_centrality", "betweenness_centrality",
                                    "hits_centrality_hub", "hits_centrality_auth"]

    """ Method to check http(s) response """

    def check_response(self, url, response):
        if response.status_code == 200:
            if self.output_msg:
                print(F"request to {url} - Successed")
            return True
        else:
            if self.output_msg:
                print(F"request to {url} - Failed")
            return False

    """ Method to construct the hashed file name of a cache record """

    def get_record_filename(self, request_path, args_list):
        args_as_sorted_tuple = tuple(args_list)
        args_as_bytes = str(args_as_sorted_tuple).encode()
        hashed_args = str(hashlib.md5(args_as_bytes).hexdigest())
        cache_key = request_path + hashed_args
        args_as_bytes = str(cache_key).encode()
        cache_record_filename = str(hashlib.md5(args_as_bytes).hexdigest())

        return cache_record_filename

    """ Methods for clearing cache records """

    def clear_cache(self, request_path, args_list):
        if self.output_msg:
            print(F"\n--> Clearing cache records...")

        # Example input to generate md5 hash name of the cache record file
        # args_list = [('centrality', 'degree_centrality'), ('crawling_date', '2021-07-20'),
        #             ('network_name', 'Test'), ('score_type', 'total'), ('submissions_type', 'New')]
        # request_path = "/influence_graph"
        cache_record_filename = self.get_record_filename(
            request_path, args_list)

        path = os.path.join(self.cache_directory_path, cache_record_filename)
        if os.path.exists(path):
            os.remove(path)
            if self.output_msg:
                print("--> Cache record deleted successfully")
                return

        if self.output_msg:
            print("--> No cache record found")

    def clearIndexPage(self):
        if self.output_msg:
            print("\n--> Clearing cache record for index page...")

        # Delete old cache records
        args_list = []
        self.clear_cache(request_path="/", args_list=args_list)

    def clearInfluenceGraph(self):
        if self.output_msg:
            print("\n--> Clearing UI cache records for this influence graph...")

        for score_type in self.score_types:
            for centrality_measure in self.centrality_measures:
                # Delete old cache records
                args_list = [('centrality', centrality_measure), ('crawling_date', self.crawling_date),
                             ('network_name', self.network_name), ('score_type', score_type), ('submissions_type', self.submissions_type)]
                self.clear_cache(request_path="/influence_graph",
                                 args_list=args_list)

    def clearActivityGraph(self):
        if self.output_msg:
            print("\n--> Refreshing UI cache records for this activity graph...")

        for score_type in self.score_types:
            # Delete old cache records
            args_list = [('crawling_date', self.crawling_date), ('network_name', self.network_name),
                         ('score_type', score_type), ('submissions_type', self.submissions_type)]
            self.clear_cache(request_path="/activity_graph",
                             args_list=args_list)

    def clearCentralityReport(self):
        if self.output_msg:
            print(
                "\n--> Clearing the UI cache record for centrality reports of this influence graph...")

        # Delete old cache records
        args_list = [('crawling_date', self.crawling_date), ('network_name',
                                                             self.network_name), ('submissions_type', self.submissions_type)]
        self.clear_cache(request_path="/centrality_report",
                         args_list=args_list)

    def clearTopicDetectionModel(self):
        if self.output_msg:
            print("\n--> Refreshing the UI cache record for evaluation and tuning of the text classifier used for influence field detection in this influence graphs...")

        # Delete old cache records
        args_list = [('crawling_date', self.crawling_date), ('network_name',
                                                             self.network_name), ('submissions_type', self.submissions_type)]
        self.clear_cache(request_path="/topic_detection_model",
                         args_list=args_list)

    def clear_system_cache(self):
        self.clearIndexPage()
        self.clearInfluenceGraph()
        self.clearActivityGraph()
        self.clearCentralityReport()
        self.clearTopicDetectionModel()

    """ Methods for refreshing cache records """

    def refreshIndexPage(self):
        if self.output_msg:
            print("\n--> Refreshing cache record for index page...")

        # Delete old cache records
        self.clearIndexPage()

        # Create new records by fetching the respective urls
        url = F"{self.domain_name}/"
        response = requests.get(url, timeout=54000)
        self.check_response(url, response)

    def refreshInfluenceGraph(self):
        if self.output_msg:
            print("\n--> Refreshing UI cache records for this influence graph...")

        # Delete old cache records
        self.clearInfluenceGraph()

        for score_type in self.score_types:
            for centrality_measure in self.centrality_measures:
                # Create new records by fetching the respective urls
                url = F"{self.domain_name}/influence_graph?network_name={self.network_name}&submissions_type={self.submissions_type}&crawling_date={self.crawling_date}&score_type={score_type}&centrality={centrality_measure}"
                response = requests.get(url, timeout=54000)
                self.check_response(url, response)

    def refreshActivityGraph(self):
        if self.output_msg:
            print("\n--> Refreshing UI cache records for this activity graph...")

        # Delete old cache records
        self.clearActivityGraph()

        for score_type in self.score_types:
            # Create new records by fetching the respective urls
            url = F"{self.domain_name}/activity_graph?network_name={self.network_name}&submissions_type={self.submissions_type}&crawling_date={self.crawling_date}&score_type={score_type}"
            response = requests.get(url, timeout=54000)
            self.check_response(url, response)

    def refreshCentralityReport(self):
        if self.output_msg:
            print(
                "\n--> Refreshing the UI cache record for centrality reports of this influence graph...")

        # Delete old cache records
        self.clearCentralityReport()

        # Create new record by fetching the respective url
        url = F"{self.domain_name}/centrality_report?network_name={self.network_name}&submissions_type={self.submissions_type}&crawling_date={self.crawling_date}"
        response = requests.get(url, timeout=54000)
        self.check_response(url, response)

    def refreshTopicDetectionModel(self):
        if self.output_msg:
            print("\n--> Refreshing the UI cache record for evaluation and tuning of the text classifier used for influence field detection in this influence graphs...")

        # Delete old cache records
        self.clearTopicDetectionModel()

        # Create new record by fetching the respective url
        url = F"{self.domain_name}/topic_detection_model?network_name={self.network_name}&submissions_type={self.submissions_type}&crawling_date={self.crawling_date}"
        response = requests.get(url, timeout=54000)
        self.check_response(url, response)

    def refresh_system_cache(self):
        self.refreshIndexPage()
        self.refreshInfluenceGraph()
        self.refreshActivityGraph()
        self.refreshCentralityReport()
        self.refreshTopicDetectionModel()
