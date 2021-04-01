from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from classes.modelling.ActivityGraphModelling import ActivityGraph
from classes.modelling.UserGraphModelling import UserGraph
from dotenv import load_dotenv
from datetime import date
import json
import os

load_dotenv()

mongo_db_connector = MongoDBConnector(
    os.environ.get('mongo_connnection_string')
)

neo4j_db_connector = GraphDBConnector(
    uri=os.environ.get('neo4j_connection_string'),
    user=os.environ.get('neo4j_username'),
    password=os.environ.get('neo4j_password'),
)

user_model = UserGraph(
    mongo_db_connector=mongo_db_connector,
    neo4j_db_connector=neo4j_db_connector
)

user_model.build(network_name="Test", submissions_type="New")

user_model.save(
    database_name=F"testusergraph{str(date.today()).replace('-','')}")

print(
    F"User Graph: #nodes: {len(user_model.nodes)}, #edges: {len(user_model.edges)}")

activity_model = ActivityGraph(
    mongo_db_connector=mongo_db_connector,
    neo4j_db_connector=neo4j_db_connector
)

activity_model.build(network_name="Test", submissions_type="New")

activity_model.save(
    database_name=F"testactivitygraph{str(date.today()).replace('-','')}")

print(
    F"Activity Graph: #nodes: {len(activity_model.nodes)}, #edges: {len(activity_model.edges)}")
