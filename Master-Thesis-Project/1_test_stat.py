from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from classes.statistics.Statistics import Statistics
from dotenv import load_dotenv
import os

load_dotenv()

mongo_db_connector = MongoDBConnector(
    os.environ.get('mongo_connnection_string')
)

# Making a neo4j graph connector
neo4j_db_connector = GraphDBConnector(
    uri=os.environ.get('neo4j_connection_string'),
    user=os.environ.get('neo4j_username'),
    password=os.environ.get('neo4j_password')
)

stat = Statistics(mongo_db_connector, neo4j_db_connector)

stat.getCrawlingRuntimes(network_name="Test Network",
                         submissions_type="New", from_date="2021-03-01")

stat.getInfluenceArea(network_name="Test",
                      submissions_type="New", model_date="2021-04-02")

stat.getInfluenceScore(network_name="Test",
                       submissions_type="New", model_date="2021-04-02", score_type="total")

stat.getInfluenceScore(network_name="Test", submissions_type="New",
                       model_date="2021-04-02", score_type=None)
