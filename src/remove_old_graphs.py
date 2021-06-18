# This script deletes all graphs that are older than 30 days
# The graphs can still be rebuilt using crawled data from mongodb

from pymongo import collation
from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from datetime import date, timedelta
from dotenv import load_dotenv
from time import time, ctime
import datetime
import logging
import os

try:
    network_name = "Reddit"
    submissions_type = "Rising"
    today_date = date.today()
    delete_older_than_date = today_date + timedelta(30)
    print(
        F"deleting all Neo4j graphs older than {str(delete_older_than_date)}")
    print(
        F"having network_name: {network_name} and submissions type = {submissions_type}")

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

    archive_databases = [
        F"{network_name}_{submissions_type}_Groups_DB",
        F"{network_name}_{submissions_type}_Submissions_DB",
        F"{network_name}_{submissions_type}_Comments_DB",
        F"{network_name}_{submissions_type}_Training_Data"
    ]
    for db in archive_databases:
        collections = mongo_db_connector.getCollectionsOfDatabase(
            database_name=db)
        for collection_name in collections:
            collection_name_split = collection_name.split("-")
            collection_date = datetime.date(int(collection_name_split[0]), int(
                collection_name_split[1]), int(collection_name_split[2]))
            if collection_date < delete_older_than_date:
                print(
                    F"deleting archive collection: {collection_name}, from database: {db}")
                mongo_db_connector.remove_collection(
                    database_name=db, collection_name=collection_name)

    # Neo4j users database connector
    neo4j_db_users_connector = GraphDBConnector(
        host=get_host('neo4j_users_db_host'),
        port=int(os.environ.get('neo4j_users_db_port')),
        user=os.environ.get('neo4j_users_db_user'),
        password=os.environ.get('neo4j_users_db_pass'),
    )

    neo4j_db_users_connector.delete_graph(
        network_name=network_name,
        submissions_type=submissions_type,
        date=str(delete_older_than_date)
    )

    # Neo4j activities database connector
    neo4j_db_activities_cconnector = GraphDBConnector(
        host=get_host('neo4j_activities_db_host'),
        port=int(os.environ.get('neo4j_activities_db_port')),
        user=os.environ.get('neo4j_activities_db_user'),
        password=os.environ.get('neo4j_activities_db_pass'),
    )

    neo4j_db_activities_cconnector.delete_graph(
        network_name=network_name,
        submissions_type=submissions_type,
        date=str(delete_older_than_date)
    )

    print("done")

except Exception as e:
    log_path = F"Logs/{str(today_date)}/{network_name}/{submissions_type}/"

    # create logs file if not found
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # create error logger
    logging.basicConfig(filename=F'{log_path}/errors.log', level=logging.INFO)

    # log error
    logging.error(F'\nError: {ctime(time())}\n{str(e)}\n', exc_info=True)
