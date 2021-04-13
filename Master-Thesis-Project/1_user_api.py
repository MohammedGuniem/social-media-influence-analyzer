from classes.database_connectors.Neo4jConnector import GraphDBConnector
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from datetime import date
import json
import os


app = Flask(__name__)

load_dotenv()

# Neo4j users database connector
neo4j_users_db_connector = GraphDBConnector(
    host=os.environ.get('neo4j_users_db_host'),
    port=int(os.environ.get('neo4j_users_db_port')),
    user=os.environ.get('neo4j_users_db_user'),
    password=os.environ.get('neo4j_users_db_pass'),
)

# Neo4j activity database connector
neo4j_activities_db_connector = GraphDBConnector(
    host=os.environ.get('neo4j_activities_db_host'),
    port=int(os.environ.get('neo4j_activities_db_port')),
    user=os.environ.get('neo4j_activities_db_user'),
    password=os.environ.get('neo4j_activities_db_pass'),
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
    user_graphs = neo4j_users_db_connector.get_graphs()
    activity_graphs = neo4j_activities_db_connector.get_graphs()
    return render_template("index.html", user_graphs=user_graphs, activity_graphs=activity_graphs)


# Example - GUI: http://localhost:5000/user_graph?graph=Test_2021-04-11&score_type=total&centrality=betweenness
# Example - JSON: http://localhost:5000/user_graph?graph=Test_2021-04-11&score_type=total&centrality=betweenness&format=json
@app.route('/user_graph')
def user_graph():
    data_format = request.args.get('format', None)
    score_type = request.args.get('score_type', "total")
    centrality = request.args.get('centrality', 'degree')
    graph = request.args.get('graph', None).split("_")
    neo4j_graph, centralities_max = neo4j_users_db_connector.get_graph(
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


# Example - GUI: http://localhost:5000/path?graph=Test_2021-04-11&score_type=total&centrality=degree&source_name=mrsbayduck&target_name=EyeHamKnotYew
# Example - JSON: http://localhost:5000/path?graph=Test_2021-04-11&score_type=total&centrality=degree&source_name=mrsbayduck&target_name=EyeHamKnotYew&format=json
@ app.route('/path')
def path():
    data_format = request.args.get('format')
    graph = request.args.get('graph', None).split("_")
    centrality = request.args.get('centrality', 'degree')
    score_type = request.args.get('score_type', "total")
    source_name = request.args.get('source_name', '')
    target_name = request.args.get('target_name', '')

    neo4j_graph, centralities_max = neo4j_users_db_connector.get_path(
        network_name=graph[0],
        date=graph[1],
        from_name=source_name,
        to_name=target_name
    )
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


# Example - GUI: http://localhost:5000/score?graph=Test_2021-04-11&score_type=total&min_score=0&max_score=10&centrality=degree
# Example - JSON: http://localhost:5000/score?graph=Test_2021-04-11&score_type=total&min_score=0&max_score=10&centrality=degree&format=json
@ app.route('/score', methods=['GET'])
def score():
    data_format = request.args.get('format')
    graph = request.args.get('graph', None).split("_")
    min_score = int(request.args.get('min_score', 0))
    max_score = int(request.args.get('max_score', 0))
    score_type = request.args.get('score_type', 'total')
    centrality = request.args.get('centrality', 'degree')

    neo4j_graph, centralities_max = neo4j_users_db_connector.filter_by_score(
        network_name=graph[0],
        date=graph[1],
        score_type=score_type,
        lower_score=min_score,
        upper_score=max_score
    )

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


# Example - GUI: http://localhost:5000/field?graph=Test_2021-04-11&score_type=total&fields=sport&fields=entertainment&operation=OR&centrality=degree
# Example - JSON: http://localhost:5000/field?graph=Test_2021-04-11&score_type=total&fields=sport&fields=entertainment&operation=OR&centrality=degree&format=json
@ app.route('/field', methods=['GET'])
def field():
    graph = request.args.get('graph', None).split("_")
    score_type = request.args.get('score_type', 'total')
    fields = request.args.to_dict(flat=False)['fields']
    operation = request.args.get('operation', 'OR')
    centrality = request.args.get('centrality', 'degree')
    data_format = request.args.get('format')

    neo4j_graph, centralities_max = neo4j_users_db_connector.filter_by_influence_area(
        network_name=graph[0],
        date=graph[1],
        areas_array=fields,
        operation=operation
    )

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


# Example - GUI: http://localhost:5000/activity_graph?graph=Test_2021-04-11&score_type=total
# Example - JSON: http://localhost:5000/activity_graph?graph=Test_2021-04-11&score_type=total&format=json
@app.route('/activity_graph')
def activity_graph():
    graph = request.args.get('graph', None).split("_")
    score_type = request.args.get('score_type', "total")
    data_format = request.args.get('format', None)

    neo4j_graph, centralities_max = neo4j_activities_db_connector.get_graph(
        network_name=graph[0], date=graph[1], relation_type="Has")
    if data_format == 'json':
        return jsonify(neo4j_graph)
    else:
        js_graph = constructJSGraph(
            neo4j_graph=neo4j_graph,
            graph_type="activity_graph",
            score_type=score_type,
            centrality_max=None
        )
    return render_template("graph.html", data=js_graph)


if __name__ == '__main__':
    app.run()
