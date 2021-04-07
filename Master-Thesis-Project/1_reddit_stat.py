from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from classes.statistics.Statistics import Statistics
from dotenv import load_dotenv
import os

load_dotenv()

mongo_db_host = os.environ.get('mongo_db_host')
mongo_db_port = os.environ.get('mongo_db_port')
mongo_db_user = os.environ.get('mongo_db_user')
mongo_db_pass = os.environ.get('mongo_db_pass')

# Mongo DB Database connector
mongo_db_connector = MongoDBConnector(
    host=mongo_db_host, port=int(mongo_db_port), user=mongo_db_user, passowrd=mongo_db_pass)

# Making a neo4j graph connector
neo4j_db_connector = GraphDBConnector(
    uri=os.environ.get('neo4j_db_connection_string'),
    user=os.environ.get('neo4j_db_username'),
    password=os.environ.get('neo4j_db_password')
)

stat = Statistics(mongo_db_connector, neo4j_db_connector)

stat.getCrawlingRuntimes(network_name="Reddit",
                         submissions_type="Rising", from_date="2021-03-01")

stat.getInfluenceArea(network_name="Reddit",
                      submissions_type="Rising", model_date="2021-04-02")

stat.getInfluenceScore(network_name="Reddit",
                       submissions_type="Rising", model_date="2021-04-02", score_type="total")

stat.getInfluenceScore(network_name="Reddit", submissions_type="Rising",
                       model_date="2021-04-02", score_type=None)
