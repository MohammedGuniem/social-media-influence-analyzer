from classes.database_connectors.Neo4jConnector import GraphDBConnector
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from datetime import date
import json
import os


app = Flask(__name__)

load_dotenv()

# Neo4j users database connector
neo4j_db_connector = GraphDBConnector(
    host=os.environ.get('neo4j_users_db_host'),
    port=int(os.environ.get('neo4j_users_db_port')),
    user=os.environ.get('neo4j_users_db_user'),
    password=os.environ.get('neo4j_users_db_pass'),
)


def constructJSGraph(neo4j_graph, graph_type, score_type, centrality_max):
    neo4j_nodes = neo4j_graph['nodes']
    neo4j_edges = neo4j_graph['links']

    js_graph = {"nodes": [], "edges": []}

    # For activity graph
    activity_colors = {
        "Submission": "yellow",
        "Top_comment": "red",
        "Sub_comment": "blue"
    }

    for node in neo4j_nodes:
        js_node = {
            "label": node['props']['name'],
            "id": node['id'],
        }
        if graph_type == "user_graph":
            js_node["value"] = node['props']['degree_centrality']
            js_node["color"] = {
                "background": F"rgba(240, 52, 52, {node['props']['degree_centrality']/centrality_max})"}
        elif graph_type == "activity_graph":
            js_node["value"] = 1
            js_node["color"] = {
                "background": activity_colors[node['props']['type']]}

        js_graph["nodes"].append(js_node)

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


# Example - GUI: http://localhost:5000/user_graph?graph=Test_2021-04-11&score_type=total&centrality=betweenness
# Example - JSON: http://localhost:5000/user_graph?graph=Test_2021-04-11&score_type=total&centrality=betweenness&format=json
@app.route('/user_graph')
def user_graph():
    data_format = request.args.get('format', None)
    score_type = request.args.get('score_type', "total")
    centrality = request.args.get('centrality', 'degree')
    graph = request.args.get('graph', None).split("_")
    neo4j_graph, centralities_max = neo4j_db_connector.get_graph(
        network_name=graph[0], date=graph[1], relation_type="Influences")

    if data_format == 'json':
        return jsonify(neo4j_graph)
    else:
        js_graph = constructJSGraph(
            neo4j_graph=neo4j_graph,
            graph_type="user_graph",
            score_type=score_type,
            centrality_max=centralities_max[centrality]
        )
    return render_template("graph.html", data=js_graph)


""" check all below """

# Example - GUI: http://localhost:5000/activity_graph?date=20210402&score_type=total
# Example - JSON: http://localhost:5000/activity_graph?date=20210402&score_type=total&format=json


@app.route('/activity_graph')
def activitygraph():
    data_format = request.args.get('format', None)
    day = request.args.get('date', None)
    score_type = request.args.get('score_type', "total")

    if day:
        day = str(day).replace('-', '')
        database_name = F"activitygraph{day}"
    else:
        database_name = "testactivitygraph"

    neo4j_graph = neo4j_db_connector.get_graph(database_name, "Has")
    if data_format == 'json':
        return jsonify(neo4j_graph)
    else:
        js_graph = constructJSGraph(
            neo4j_graph, database_name, None, score_type)
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


# Example: http://localhost:5000/degree_centrality?network_date=Test_2021-04-08&score_type=total
@ app.route('/degree_centrality', methods=['GET'])
def degree_centrality():
    network_date = request.args.get('network_date', None).split("_")
    network_name = network_date[0]
    date = network_date[1]
    score_type = request.args.get('score_type', 'total')
    degree_centrality = neo4j_db_connector.get_degree_centrality(
        network_name, date, score_type)
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
