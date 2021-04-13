from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from classes.modelling.ActivityGraphModelling import ActivityGraph
from classes.modelling.UserGraphModelling import UserGraph
from dotenv import load_dotenv
from datetime import date
import json
import os

load_dotenv()

# Mongo db database connector
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

user_model = UserGraph(
    mongo_db_connector=mongo_db_connector,
    neo4j_db_connector=neo4j_db_connector
)

user_model.build(network_name="Reddit", submissions_type="Rising")

user_model.save(graph_type="user_graph",
                network_name="Reddit", date=str(date.today()))

print(
    F"User Graph: #nodes: {len(user_model.nodes)}, #edges: {len(user_model.edges)}")

# Neo4j activities database connector
neo4j_db_connector = GraphDBConnector(
    host=os.environ.get('neo4j_activities_db_host'),
    port=int(os.environ.get('neo4j_activities_db_port')),
    user=os.environ.get('neo4j_activities_db_user'),
    password=os.environ.get('neo4j_activities_db_pass'),
)

activity_model = ActivityGraph(
    mongo_db_connector=mongo_db_connector,
    neo4j_db_connector=neo4j_db_connector
)

activity_model.build(network_name="Reddit", submissions_type="Rising")

activity_model.save(graph_type="activity_graph",
                    network_name="Reddit", date=str(date.today()))

print(
    F"Activity Graph: #nodes: {len(activity_model.nodes)}, #edges: {len(activity_model.edges)}")
