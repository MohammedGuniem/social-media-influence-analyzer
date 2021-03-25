from classes.database_connectors.Neo4jConnector import GraphDBConnector
from dotenv import load_dotenv
import os

load_dotenv()

# Making a neo4j graph connector
neo4j_db_connector = GraphDBConnector(
    uri=os.environ.get('neo4j_connection_string'),
    user=os.environ.get('neo4j_username'),
    password=os.environ.get('neo4j_password'),
    database_name="testusergraph20210323"
)

database_name = "testusergraph20210323"

print("------------------All graph--------------------")
graph = neo4j_db_connector.get_graph(database=database_name)
print("------------------nodes--------------------")
nodes = graph['nodes']
print(F"#nodes: {len(nodes)}")
for node in nodes:
    # {'id': 'U_3', 'props': {'name': 'User C', 'author_id': 'U_3'}}
    print(node['id'] + " " + node['props']['name'])

print("------------------links--------------------")
links = graph['links']
print(F"#links: {len(links)}")
for link in graph['links']:
    print(F"{link['source']} --> {link['target']}")

print()
print("---------a path from User G to User F--------------------")
path = neo4j_db_connector.get_path(
    from_name="User G", to_name="User F", database=database_name)

print("------------------nodes--------------------")
nodes = path['nodes']
print(F"#nodes: {len(nodes)}")
for node in nodes:
    # {'id': 'U_3', 'props': {'name': 'User C', 'author_id': 'U_3'}}
    print(node['id'] + " " + node['props']['name'])

print("------------------links--------------------")
links = path['links']
print(F"#links: {len(links)}")
for link in links:
    print(F"{link['source']} --> {link['target']}")


print()
print("---------filter by total score between 1 and 10--------------------")
filter_graph = neo4j_db_connector.filter_by_score(
    "all_influence_score", 0, 10, database=database_name)

print("------------------nodes--------------------")
nodes = filter_graph['nodes']
print(F"#nodes: {len(nodes)}")
for node in nodes:
    # {'id': 'U_3', 'props': {'name': 'User C', 'author_id': 'U_3'}}
    print(node['id'] + " " + node['props']['name'])

print("------------------links--------------------")
links = filter_graph['links']
print(F"#links: {len(links)}")
for link in links:
    print(F"{link['source']} --> {link['target']}")


print()
print("---------filter by influence area sport and entertainment--------------------")
filter_graph = neo4j_db_connector.filter_by_influence_area(
    ['sport', 'entertainment'], operation="AND", database=database_name)

print("------------------nodes--------------------")
nodes = filter_graph['nodes']
print(F"#nodes: {len(nodes)}")
for node in nodes:
    # {'id': 'U_3', 'props': {'name': 'User C', 'author_id': 'U_3'}}
    print(node['id'] + " " + node['props']['name'])

print("------------------links--------------------")
links = filter_graph['links']
print(F"#links: {len(links)}")
for link in links:
    print(F"{link['source']} --> {link['target']}")
