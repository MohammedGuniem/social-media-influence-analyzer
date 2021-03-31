from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
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

model = UserGraph(
    mongo_db_connector=mongo_db_connector,
    neo4j_db_connector=neo4j_db_connector
)

model.build(network_name="Reddit", submissions_type="Rising")

model.save(database_name=F"usergraph{str(date.today()).replace('-','')}")

print(len(model.nodes))
