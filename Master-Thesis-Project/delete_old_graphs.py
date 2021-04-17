# This script deletes all graphs that are older than 30 days
# The graphs can still be rebuilt using crawled data from mongodb

from classes.database_connectors.Neo4jConnector import GraphDBConnector
from datetime import date, timedelta
from dotenv import load_dotenv
from time import time, ctime
import logging
import os

try:
    network_name = "Reddit"
    today_date = date.today()
    delete_older_than_date = str(today_date - timedelta(30))

    load_dotenv()

    # Neo4j users database connector
    neo4j_db_users_connector = GraphDBConnector(
        host=os.environ.get('neo4j_users_db_host'),
        port=int(os.environ.get('neo4j_users_db_port')),
        user=os.environ.get('neo4j_users_db_user'),
        password=os.environ.get('neo4j_users_db_pass'),
    )

    neo4j_db_users_connector.delete_graph(
        network_name=network_name,
        date=delete_older_than_date
    )

    # Neo4j activities database connector
    neo4j_db_activities_cconnector = GraphDBConnector(
        host=os.environ.get('neo4j_activities_db_host'),
        port=int(os.environ.get('neo4j_activities_db_port')),
        user=os.environ.get('neo4j_activities_db_user'),
        password=os.environ.get('neo4j_activities_db_pass'),
    )

    neo4j_db_activities_cconnector.delete_graph(
        network_name=network_name,
        date=delete_older_than_date
    )

except Exception as e:
    log_path = F"Logs/{network_name}/{str(today_date)}/"

    # create logs file if not found
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # create error logger
    logging.basicConfig(filename=F'{log_path}/errors.log', level=logging.INFO)

    # log error
    logging.error(F'\nError: {ctime(time())}\n{str(e)}\n', exc_info=True)
