import statistics
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from dotenv import load_dotenv
from datetime import date
import json
import os

load_dotenv()

# Making a neo4j graph connector
neo4j_db_connector = GraphDBConnector(
    uri=os.environ.get('neo4j_db_connection_string'),
    user=os.environ.get('neo4j_db_username'),
    password=os.environ.get('neo4j_db_password'),
    database_name="testusergraph20210323"
)

database_name = "testusergraph20210323"

print()
print("Degree Centrality, normalized, weighted and directed")
centrality = neo4j_db_connector.get_degree_centrality(
    database=database_name, score_type="all_influence_score")
print(centrality.keys())
print(centrality.values())

print()
print("Betweenness Centrality, normalized, unweighted and directed")
centrality = neo4j_db_connector.get_betweenness_centrality(
    database=database_name)
print(centrality.keys())
print(centrality.values())

print()
print("HITS Centrality, normalized, unweighted and directed")
centrality, hitsIterations = neo4j_db_connector.get_hits_centrality(
    database=database_name)
print(centrality.keys())
print(centrality.values())
print(F"converged after {hitsIterations} hitsIteration")

"""
def merge_centrality_scores(*ordered_users):
    users = {}
    for user_array in ordered_users:
        top_score = len(user_array)
        for user in user_array:
            if user not in users:
                users[user] = [top_score - user_array.index(user)]
            else:
                users[user].append(top_score - user_array.index(user))
    merged_scores = {}
    for user, scores in users.items():
        merged_scores[user] = round(statistics.median(scores))
    return merged_scores

merged_centrality_scores = merge_centrality_scores(degree_ordered_users, betweennes_ordered_users,
                                                   auth_hits_ordered_users, hub_hits_ordered_users)

print()
for user, score in sorted(merged_centrality_scores.items(), key=lambda item: item[1], reverse=True):
    print(F"{user} - {score}")
"""
