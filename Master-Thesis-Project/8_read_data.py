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

"""
print("------------------All graph--------------------")
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

"""

print("------------------a path--------------------")
path = neo4j_db_connector.get_path(
    from_name="User G", to_name="User F", shortestPath=False)

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
    """
    {'source': 'U_3', 'target': 'U_6',
         'props': {
            'influence_areas': ['entertainment', 'sport'], 
            'influence_scores': {  'connection': 3, 
                                    'activity': 3, 
                                    'upvotes': 27, 
                                    'connection_and_activity': 6, 
                                    'connection_and_upvotes': 30, 
                                    'activity_and_upvotes': 30, 
                                    'all': 33
                                },
            'subreddits': ['Test', 'Test_2']
            }
        }
    """
    print(F"{link['source']} --> {link['target']}")
