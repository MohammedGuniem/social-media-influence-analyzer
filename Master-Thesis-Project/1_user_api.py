from classes.database_connectors.Neo4jConnector import GraphDBConnector
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from datetime import date
import json
import os


app = Flask(__name__)

load_dotenv()

# Making a neo4j graph connector
neo4j_db_connector = GraphDBConnector(
    uri=os.environ.get('neo4j_connection_string'),
    user=os.environ.get('neo4j_username'),
    password=os.environ.get('neo4j_password'),
    database_name="testusergraph20210402"
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
            "color": "rgba(50, 121, 168)",
            "value": edge['props'][score_type],
            "label": F"{str(edge['props'][score_type])}\\n{', '.join(edge['props']['influence_areas'])}"
        })

    return js_graph


@app.route('/')
def index():
    user_graphs = neo4j_db_connector.get_user_graphs()
    return render_template("index.html", user_graphs=user_graphs)


# Example - GUI: http://localhost:5000/graph?date=20210402&score_type=total&centrality=degree
# Example - JSON: http://localhost:5000/graph?date=20210402&score_type=total&centrality=degree&format=json
@app.route('/graph')
def graph():
    data_format = request.args.get('format', None)
    day = request.args.get('date', None)
    centrality = request.args.get('centrality', 'degree')
    score_type = request.args.get('score_type', "total")

    if day:
        day = str(day).replace('-', '')
        database_name = F"usergraph{day}"
    else:
        database_name = "testusergraph"

    neo4j_graph = neo4j_db_connector.get_graph(database_name)
    if data_format == 'json':
        return jsonify(neo4j_graph)
    else:
        js_graph = constructJSGraph(
            neo4j_graph, database_name, centrality, score_type)
    return render_template("graph.html", data=js_graph)


# Example - GUI: http://localhost:5000/activitygraph?date=20210402&score_type=total&centrality=degree
# Example - JSON: http://localhost:5000/activitygraph?date=20210402&score_type=total&centrality=degree&format=json
@app.route('/activitygraph')
def activitygraph():
    data_format = request.args.get('format', None)
    day = request.args.get('date', None)
    centrality = request.args.get('centrality', 'degree')
    score_type = request.args.get('score_type', "total")

    if day:
        day = str(day).replace('-', '')
        database_name = F"activitygraph{day}"
    else:
        database_name = "testactivitygraph"

    neo4j_graph = neo4j_db_connector.get_graph(database_name)
    if data_format == 'json':
        return jsonify(neo4j_graph)
    else:
        js_graph = constructJSGraph(
            neo4j_graph, database_name, centrality, score_type)
    return render_template("graph.html", data=js_graph)


# Example - GUI: http://localhost:5000/path?date=20210402&score_type=total&source_name=What_the_hellll&target_name=Golden_Renegade&centrality=degree
# Example - JSON: http://localhost:5000/path?date=20210402&score_type=total&source_name=What_the_hellll&target_name=Golden_Renegade&centrality=degree&format=json
@ app.route('/path')
def path():
    data_format = request.args.get('format')
    day = str(request.args.get('date', str(date.today()))).replace('-', '')
    database_name = F"usergraph{day}"
    centrality = request.args.get('centrality', 'degree')
    score_type = request.args.get('score_type', "total")
    source_name = request.args.get('source_name', '')
    target_name = request.args.get('target_name', '')

    neo4j_graph = neo4j_db_connector.get_path(
        source_name, target_name, database_name)
    if data_format == 'json':
        return jsonify(neo4j_graph)
    else:
        js_graph = constructJSGraph(
            neo4j_graph, database_name, centrality, score_type)
    return render_template("graph.html", data=js_graph)


# Example - GUI: http://localhost:5000/score?date=20210402&score_type=total&min_score=0&centrality=degree&max_score=10
# Example - JSON: http://localhost:5000/score?date=20210402&score_type=total&min_score=0&max_score=10&centrality=degree&format=json
@ app.route('/score', methods=['GET'])
def score():
    data_format = request.args.get('format')
    day = str(request.args.get('date', str(date.today()))).replace('-', '')
    database_name = F"usergraph{day}"
    centrality = request.args.get('centrality', 'degree')
    score_type = request.args.get('score_type', 'total')
    min_score = int(request.args.get('min_score', 0))
    max_score = int(request.args.get('max_score', 0))

    neo4j_graph = neo4j_db_connector.filter_by_score(
        score_type, min_score, max_score, database_name)

    if data_format == 'json':
        return jsonify(neo4j_graph)
    else:
        js_graph = constructJSGraph(
            neo4j_graph, database_name, centrality, score_type)
    return render_template("graph.html", data=js_graph)


# Example - GUI: http://localhost:5000/field?date=20210402&score_type=total&fields=sport&fields=entertainment&operation=OR&centrality=degree
# Example - JSON: http://localhost:5000/field?date=20210402&score_type=total&fields=sport&fields=entertainment&operation=OR&centrality=degree&format=json
@ app.route('/field', methods=['GET'])
def field():
    data_format = request.args.get('format')
    day = str(request.args.get('date', str(date.today()))).replace('-', '')
    database_name = F"usergraph{day}"
    centrality = request.args.get('centrality', 'degree')
    score_type = request.args.get('score_type', 'total')
    fields = request.args.to_dict(flat=False)['fields']
    operation = request.args.get('operation', 'OR')

    neo4j_graph = neo4j_db_connector.filter_by_influence_area(
        fields, operation, database_name)

    if data_format == 'json':
        return jsonify(neo4j_graph)
    else:
        js_graph = constructJSGraph(
            neo4j_graph, database_name, centrality, score_type)
    return render_template("graph.html", data=js_graph)


# Example: http://localhost:5000/degree_centrality?date=20210402&score_type=total
@ app.route('/degree_centrality', methods=['GET'])
def degree_centrality():
    score_type = request.args.get('score_type', 'total')
    day = str(request.args.get('date', str(date.today()))).replace('-', '')
    database_name = F"usergraph{day}"
    degree_centrality = neo4j_db_connector.get_degree_centrality(
        database_name, score_type)
    return jsonify(degree_centrality)


# Example: http://localhost:5000/betweenness_centrality?date=20210402
@ app.route('/betweenness_centrality', methods=['GET'])
def betweenness_centrality():
    day = str(request.args.get('date', str(date.today()))).replace('-', '')
    database_name = F"usergraph{day}"
    betweennes_centrality = neo4j_db_connector.get_betweenness_centrality(
        database_name)
    return jsonify(betweennes_centrality)


# Example: http://localhost:5000/hits_centrality?date=20210402
@ app.route('/hits_centrality', methods=['GET'])
def hits_centrality():
    day = str(request.args.get('date', str(date.today()))).replace('-', '')
    database_name = F"usergraph{day}"
    hits_centrality, hitsIterations = neo4j_db_connector.get_hits_centrality(
        database_name)
    return jsonify({'centralities': hits_centrality, 'hitsIterations': hitsIterations})


if __name__ == '__main__':
    app.run()
