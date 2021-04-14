from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from classes.statistics.Statistics import Statistics
from dotenv import load_dotenv
import os

load_dotenv()

# Mongo database connector
mongo_db_connector = MongoDBConnector(
    host=os.environ.get('mongo_db_host'),
    port=int(os.environ.get('mongo_db_port')),
    user=os.environ.get('mongo_db_user'),
    passowrd=os.environ.get('mongo_db_pass')
)

# Neo4j users database connector
neo4j_db_connector = GraphDBConnector(
    host=os.environ.get('neo4j_users_db_host'),
    port=int(os.environ.get('neo4j_users_db_port')),
    user=os.environ.get('neo4j_users_db_user'),
    password=os.environ.get('neo4j_users_db_pass'),
)

stat = Statistics(mongo_db_connector, neo4j_db_connector)

stat.getCrawlingRuntimes(network_name="Test",
                         submissions_type="New", from_date="2021-04-14")

stat.getInfluenceArea(network_name="Test",
                      submissions_type="New", model_date="2021-04-14")

for score_type in ["interaction", "activity", "upvotes", "interaction_and_activity", "activity_and_upvotes", "interaction_and_upvotes", "total"]:
    stat.getInfluenceScore(network_name="Test",
                           model_date="2021-04-14", score_type=score_type)

stat.getInfluenceScore(network_name="Test",
                       model_date="2021-04-14", score_type=None)
