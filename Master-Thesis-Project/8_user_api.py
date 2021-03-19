from classes.database_connectors.Neo4jConnector import GraphDBConnector
from dotenv import load_dotenv
from flask import Flask, jsonify
import json
import os


app = Flask(__name__)

load_dotenv()

# Making a neo4j graph connector
neo4j_db_connector = GraphDBConnector(
    uri=os.environ.get('neo4j_connection_string'),
    user=os.environ.get('neo4j_username'),
    password=os.environ.get('neo4j_password'),
    database_name="testusergraph20210318"
)


@app.route('/')
def index():
    return "Index Page"


# Example: http://localhost:5000/graph/testusergraph20210318
@app.route('/graph/<database_name>', methods=['GET'])
def graph(database_name):
    graph = neo4j_db_connector.get_graph(database=database_name)
    return jsonify(graph)


# Example: http://localhost:5000/path/User%20G/User%20F/True/testusergraph20210318
@app.route('/path/<from_username>/<to_username>/<is_shortestpath>/<database_name>', methods=['GET'])
def path(from_username, to_username, is_shortestpath, database_name):
    path = neo4j_db_connector.get_path(
        from_name=from_username, to_name=to_username, shortestPath=is_shortestpath, database=database_name)
    return jsonify(path)


# Example: http://localhost:5000/filter_by_score/all_influence_score/0/10/testusergraph20210318
@app.route('/filter_by_score/<score_type>/<int:min>/<int:max>/<database_name>', methods=['GET'])
def filter_by_score(score_type, min, max, database_name):
    filter_graph = neo4j_db_connector.filter_by_score(
        score_type, min, max, database=database_name)
    return jsonify(filter_graph)


# Example: http://localhost:5000/filter_by_influence_area/sport&entertainment/AND/testusergraph20210318
@app.route('/filter_by_influence_area/<influence_area>/<operation>/<database_name>', methods=['GET'])
def filter_by_influence_area(influence_area, operation, database_name):
    filter_graph = neo4j_db_connector.filter_by_influence_area(
        influence_area.split("&"), operation, database=database_name)
    return jsonify(filter_graph)


# Example: http://localhost:5000/degree_centrality/testusergraph20210318
@app.route('/degree_centrality/<database_name>', methods=['GET'])
def degree_centrality(database_name):
    degree_ordered_users, degree_ordered_user_centrality = neo4j_db_connector.get_degree_centrality(
        database=database_name)
    degree_centrality = {'users': degree_ordered_users,
                         'users_centrality': degree_ordered_user_centrality}
    return jsonify(degree_centrality)


# Example: http://localhost:5000/betweenness_centrality/testusergraph20210318
@app.route('/betweenness_centrality/<database_name>', methods=['GET'])
def betweenness_centrality(database_name):
    betweennes_ordered_users, betweennes_ordered_user_centrality = neo4j_db_connector.get_betweenness_centrality(
        database=database_name)

    betweennes_centrality = {
        'users': betweennes_ordered_users,
        'users_centrality': betweennes_ordered_user_centrality
    }
    return jsonify(betweennes_centrality)


# Example: http://localhost:5000/hits_centrality/AUTH/testusergraph20210318
# Example: http://localhost:5000/hits_centrality/HUB/testusergraph20210318
@app.route('/hits_centrality/<order_by>/<database_name>', methods=['GET'])
def hits_centrality(order_by, database_name):
    hits_ordered_users, hits_ordered_user_centrality, hitsIterations = neo4j_db_connector.get_hits_centrality(
        order_by=order_by, database=database_name)

    hits_centrality = {
        'users': hits_ordered_users,
        'users_centrality': hits_ordered_user_centrality,
        'NumberOfIterationsNeededToConverge': hitsIterations
    }
    return jsonify(hits_centrality)


if __name__ == '__main__':
    app.run()
