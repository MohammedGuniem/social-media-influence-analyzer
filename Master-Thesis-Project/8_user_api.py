from classes.database_connectors.Neo4jConnector import GraphDBConnector
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
import json
import os


app = Flask(__name__)

load_dotenv()

# Making a neo4j graph connector
neo4j_db_connector = GraphDBConnector(
    uri=os.environ.get('neo4j_connection_string'),
    user=os.environ.get('neo4j_username'),
    password=os.environ.get('neo4j_password'),
    database_name="testusergraph20210323"
)


def constructJSGraph(neo4j_graph, database_name, centrality, score_type):
    if centrality == "betweenness":
        centralities = neo4j_db_connector.get_betweenness_centrality(
            database_name)
    elif centrality.split("-")[0] == "hits":
        hits_centralities, _ = neo4j_db_connector.get_hits_centrality(
            database_name)
        centralities = {}

        for k, v in hits_centralities.items():
            centralities[k] = hits_centralities[k][centrality.split("-")[1]]
    else:
        centralities = neo4j_db_connector.get_degree_centrality(
            database_name, score_type)

    neo4j_nodes = neo4j_graph['nodes']
    neo4j_edges = neo4j_graph['links']

    js_graph = {"nodes": [], "edges": []}

    for node in neo4j_nodes:
        js_graph["nodes"].append({
            "label": node['props']['name'],
            "id": node['id'],
            "value": centralities[node['props']['name']],
            "color": {"background": F"rgba(240, 52, 52, {centralities[node['props']['name']]})"}
        })

    for edge in neo4j_edges:
        js_graph["edges"].append({
            "from": edge['source'],
            "to": edge['target'],
            "value": edge['props'][score_type],
            "label": str(edge['props'][score_type])
        })

    return js_graph


# Example - GUI: http://localhost:5000/?database_name=testusergraph20210323&score_type=all_influence_score&centrality=degree
# Example - JSON: http://localhost:5000/?database_name=testusergraph20210323&score_type=all_influence_score&centrality=degree&format=json
@app.route('/')
def index():
    data_format = request.args.get('format')
    database_name = request.args.get('database_name') if request.args.get(
        'database_name') else "testusergraph20210323"
    centrality = request.args.get('centrality')
    score_type = request.args.get('score_type')

    neo4j_graph = neo4j_db_connector.get_graph(database_name)
    if data_format == 'json':
        return jsonify(neo4j_graph)
    else:
        js_graph = constructJSGraph(
            neo4j_graph, database_name, centrality, score_type)
    return render_template("index.html", data=js_graph)


# Example - GUI: http://localhost:5000/path?database_name=testusergraph20210323&score_type=all_influence_score&source_name=User%20F&target_name=User%20E&centrality=degree
# Example - JSON: http://localhost:5000/path?database_name=testusergraph20210323&score_type=all_influence_score&source_name=User%20F&target_name=User%20E&centrality=degree&format=json
@app.route('/path')
def path():
    data_format = request.args.get('format')
    database_name = request.args.get('database_name') if request.args.get(
        'database_name') else "testusergraph20210323"
    centrality = request.args.get('centrality')
    source_name = request.args.get('source_name')
    target_name = request.args.get('target_name')
    score_type = request.args.get('score_type')

    neo4j_graph = neo4j_db_connector.get_path(
        source_name, target_name, database_name)
    if data_format == 'json':
        return jsonify(neo4j_graph)
    else:
        js_graph = constructJSGraph(
            neo4j_graph, database_name, centrality, score_type)
    return render_template("index.html", data=js_graph)


# Example - GUI: http://localhost:5000/filter_by_score?database_name=testusergraph20210323&score_type=all_influence_score&min_score=0&centrality=degree&max_score=10
# Example - JSON: http://localhost:5000/filter_by_score?database_name=testusergraph20210323&score_type=all_influence_score&min_score=0&max_score=10&centrality=degree&format=json
@ app.route('/filter_by_score', methods=['GET'])
def filter_by_score():
    data_format = request.args.get('format')
    database_name = request.args.get('database_name') if request.args.get(
        'database_name') else "testusergraph20210323"
    score_type = request.args.get('score_type')
    min_score = int(request.args.get('min_score'))
    max_score = int(request.args.get('max_score'))
    centrality = request.args.get('centrality')

    neo4j_graph = neo4j_db_connector.filter_by_score(
        score_type, min_score, max_score, database_name)

    if data_format == 'json':
        return jsonify(neo4j_graph)
    else:
        js_graph = constructJSGraph(
            neo4j_graph, database_name, centrality, score_type)
    return render_template("index.html", data=js_graph)


# Example - GUI: http://localhost:5000/filter_by_influence_area?database_name=testusergraph20210323&score_type=all_influence_score&influence_areas=sport%20entertainment&operation=AND&centrality=degree
# Example - JSON: http://localhost:5000/filter_by_influence_area?database_name=testusergraph20210323&score_type=all_influence_score&influence_areas=sport%20entertainment&operation=AND&centrality=degree&format=json
@ app.route('/filter_by_influence_area', methods=['GET'])
def filter_by_influence_area():
    data_format = request.args.get('format')
    database_name = request.args.get('database_name') if request.args.get(
        'database_name') else "testusergraph20210323"
    influence_areas = request.args.get('influence_areas').split(" ")
    operation = request.args.get('operation')
    centrality = request.args.get('centrality')
    score_type = request.args.get('score_type')

    neo4j_graph = neo4j_db_connector.filter_by_influence_area(
        influence_areas, operation, database_name)

    if data_format == 'json':
        return jsonify(neo4j_graph)
    else:
        js_graph = constructJSGraph(
            neo4j_graph, database_name, centrality, score_type)
    return render_template("index.html", data=js_graph)


# Example: http://localhost:5000/degree_centrality/testusergraph20210323?score_type=all_influence_score
@ app.route('/degree_centrality/<database_name>', methods=['GET'])
def degree_centrality(database_name):
    score_type = request.args.get('score_type')
    degree_centrality = neo4j_db_connector.get_degree_centrality(
        database_name, score_type)
    return jsonify(degree_centrality)


# Example: http://localhost:5000/betweenness_centrality/testusergraph20210323
@ app.route('/betweenness_centrality/<database_name>', methods=['GET'])
def betweenness_centrality(database_name):
    betweennes_centrality = neo4j_db_connector.get_betweenness_centrality(
        database_name)
    return jsonify(betweennes_centrality)


# Example: http://localhost:5000/hits_centrality/testusergraph20210323
@ app.route('/hits_centrality/<database_name>', methods=['GET'])
def hits_centrality(database_name):
    hits_centrality, hitsIterations = neo4j_db_connector.get_hits_centrality(
        database_name)
    return jsonify({'centralities': hits_centrality, 'hitsIterations': hitsIterations})


if __name__ == '__main__':
    app.run()
