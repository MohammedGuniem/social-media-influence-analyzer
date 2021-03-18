from classes.database_connectors.Neo4jConnector import GraphDBConnector
from dotenv import load_dotenv
from datetime import date
import json
import os

load_dotenv()

# Making a neo4j graph connector
neo4j_db_connector = GraphDBConnector(
    uri=os.environ.get('neo4j_connection_string'),
    user=os.environ.get('neo4j_username'),
    password=os.environ.get('neo4j_password'),
    database_name="testusergraph20210318"
)

print()
print("Degree Centrality, normalized, weighted and directed")
dc_ordered_users, dc_ordered_user_centrality = neo4j_db_connector.get_degree_centrality()
print(dc_ordered_users)
print(dc_ordered_user_centrality)

print()
print("Degree Centrality, normalized, unweighted and directed")
bc_ordered_users, bc_ordered_user_centrality = neo4j_db_connector.get_betweenness_centrality()
print(bc_ordered_users)
print(bc_ordered_user_centrality)
