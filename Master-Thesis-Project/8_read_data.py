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
    database_name="testusergraph20210309"
)

graph = neo4j_db_connector.get_graph()
print("------------------nodes--------------------")
nodes = graph['nodes']
print(F"#nodes: {len(nodes)}")
for n in nodes:
    print(n)

element_nr = 4
print()
print(nodes[element_nr]['props'])

print()
print(nodes[element_nr]['props']['name'])
print(nodes[element_nr]['props']['author_id'])

print("------------------links--------------------")
links = graph['links']
print(F"#links: {len(links)}")
for l in graph['links']:
    print(l)

element_nr = 4
print()
print(links[element_nr]['props'])

print()
print(links[element_nr]['props']['subreddits'])
print(links[element_nr]['props']['subreddits'][1])

print()
print(links[element_nr]['props']['influence_areas'])
print(links[element_nr]['props']['influence_areas'][1])

print()
print(links[element_nr]['props']['influence_scores'])
print(links[element_nr]['props']['influence_scores']
      ['connection_and_activity'])
