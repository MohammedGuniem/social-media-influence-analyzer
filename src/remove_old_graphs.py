from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from datetime import date, timedelta
from dotenv import load_dotenv
from time import time, ctime
import datetime
import logging
import shutil
import os

try:

    exec_plan = {
        "deletion_1": {
            "network_name": "Test",
            "submissions_type": "New",
            "delete_from_date": "2021-06-15",
            "delete_to_date": "2021-06-25",
            "delete_on": ["mongo_db_archive", "runtime_register", "statistics_plots", "neo4j_users_graph", "neo4j_activities_graph"]
        },
        "deletion_2": {
            "network_name": "Reddit",
            "submissions_type": "New",
            "delete_from_date": "2021-06-15",
            "delete_to_date": "2021-06-25",
            "delete_on": ["mongo_db_archive", "runtime_register", "statistics_plots", "neo4j_users_graph", "neo4j_activities_graph"]
        },
        "deletion_3": {
            "network_name": "Reddit",
            "submissions_type": "Rising",
            "delete_from_date": "2021-06-15",
            "delete_to_date": "2021-06-25",
            "delete_on": ["mongo_db_archive", "runtime_register", "statistics_plots", "neo4j_users_graph", "neo4j_activities_graph"]
        },
        "deletion_4": {
            "network_name": "Selective_Reddit",
            "submissions_type": "New",
            "delete_from_date": "2021-06-15",
            "delete_to_date": "2021-06-25",
            "delete_on": ["mongo_db_archive", "runtime_register", "statistics_plots", "neo4j_users_graph", "neo4j_activities_graph"]
        },
        "deletion_5": {
            "network_name": "Selective_Reddit",
            "submissions_type": "Rising",
            "delete_from_date": "2021-06-15",
            "delete_to_date": "2021-06-25",
            "delete_on": ["mongo_db_archive", "runtime_register", "statistics_plots", "neo4j_users_graph", "neo4j_activities_graph"]
        }
    }

    load_dotenv()

    def get_host(target):
        if os.environ.get('IS_DOCKER') == "True":
            return "host.docker.internal"
        return os.environ.get(target)

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

    for deletion_id, config in exec_plan.items():

        network_name = config["network_name"]
        submissions_type = config["submissions_type"]
        delete_from_date = config["delete_from_date"]
        delete_to_date = config["delete_to_date"]
        delete_on = config["delete_on"]

        from_date = datetime.datetime.strptime(delete_from_date, '%Y-%m-%d')
        to_date = datetime.datetime.strptime(delete_to_date, '%Y-%m-%d')

        current_loop_date = from_date
        while True:
            if current_loop_date <= to_date:
                if "mongo_db_archive" in delete_on:
                    archive_databases = [
                        F"{network_name}_{submissions_type}_Groups_DB",
                        F"{network_name}_{submissions_type}_Submissions_DB",
                        F"{network_name}_{submissions_type}_Comments_DB",
                        F"{network_name}_{submissions_type}_Training_Data"
                    ]
                    collection_name = current_loop_date.strftime("%Y-%m-%d")
                    for db in archive_databases:
                        delete_count = mongo_db_connector.remove_collection(
                            database_name=db, collection_name=collection_name)
                        if delete_count > 0:
                            print(
                                F"Removed archive_database: {db}, archive_collection: {collection_name}")
                            print()

                            if "statistics_plots" in delete_on:
                                crawling_plot_folder = F"statistics_plots/crawling/{network_name}/{collection_name}/{submissions_type}"
                                influence_areas_plot_folder = F"statistics_plots/influence_areas_and_subreddits/{network_name}/{collection_name}/{submissions_type}"
                                influence_score_plot_folder = F"statistics_plots/influence_scores/{network_name}/{collection_name}/{submissions_type}"
                                for plot_folder in [crawling_plot_folder, influence_areas_plot_folder, influence_score_plot_folder]:
                                    try:
                                        shutil.rmtree(plot_folder)
                                        print(
                                            F"Deleted statistics plot from: {plot_folder}")
                                        print()
                                    except OSError as e:
                                        continue

                current_loop_date = current_loop_date + timedelta(1)
            else:
                break

        if "runtime_register" in delete_on:
            delete_count = mongo_db_connector.remove_crawling_runtime(
                network_name,
                submissions_type,
                from_timestamp=int(datetime.datetime.timestamp(from_date)),
                to_timestamp=int(datetime.datetime.timestamp(to_date))
            )
            if delete_count > 0:
                print(
                    F"deleted {delete_count} item(s) from crawling_runtime_register")
                print()

        if "neo4j_users_graph" in delete_on:
            nodes_deleted, relationships_deleted = neo4j_db_users_connector.delete_graph(
                network_name=network_name,
                submissions_type=submissions_type,
                from_date=from_date.strftime("%Y-%m-%d"),
                to_date=to_date.strftime("%Y-%m-%d")
            )
            if nodes_deleted > 0 or relationships_deleted > 0:
                print(
                    F"Deleted users graph: {nodes_deleted} nodes, {relationships_deleted} relationships\nfrom network: {network_name}, submissions type: {submissions_type} \n from {from_date} to {to_date}")
                print()

        if "neo4j_activities_graph" in delete_on:
            nodes_deleted, relationships_deleted = neo4j_db_activities_connector.delete_graph(
                network_name=network_name,
                submissions_type=submissions_type,
                from_date=from_date.strftime("%Y-%m-%d"),
                to_date=to_date.strftime("%Y-%m-%d")
            )
            if nodes_deleted > 0 or relationships_deleted > 0:
                print(
                    F"Deleted activity graph: {nodes_deleted} nodes, {relationships_deleted} relationships\nfrom network: {network_name}, submissions type: {submissions_type} \n from {from_date} to {to_date}")
                print()

except Exception as e:
    today_date = date.today()
    log_path = F"Logs/{str(today_date)}/{network_name}/{submissions_type}/"

    # create logs file if not found
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # create error logger
    logging.basicConfig(filename=F'{log_path}/errors.log', level=logging.INFO)

    # log error
    logging.error(F'\nError: {ctime(time())}\n{str(e)}\n', exc_info=True)
