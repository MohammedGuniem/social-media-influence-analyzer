from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from classes.modelling.UserGraphModelling import UserGraph
from dotenv import load_dotenv
import json
import os

load_dotenv()

mongo_db_connector = MongoDBConnector(
    os.environ.get('mongo_connnection_string'),
    collection_name="2021-03-29"
)

neo4j_db_connector = GraphDBConnector(
    uri=os.environ.get('neo4j_connection_string'),
    user=os.environ.get('neo4j_username'),
    password=os.environ.get('neo4j_password'),
)

model = UserGraph(
    mongo_db_connector=mongo_db_connector,
    neo4j_db_connector=neo4j_db_connector
)

network_name = "Test"

for group in mongo_db_connector.getGroups(network_name):
    model.build_model(network_name=network_name,
                      group_name=group['display_name'],
                      submissions_type="New")
