from classes.database_connectors.Neo4jConnector import GraphDBConnector
from flask import Flask, jsonify, render_template, request, send_file
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
            node_type = node['props']['type']
            js_node["label"] = F"{node_type}\\n{js_node['label']}"
            js_node["value"] = 1
            js_node["color"] = {
                "background": activity_colors[node_type]
            }

        js_graph["nodes"].append(js_node)

    for edge in neo4j_edges:
        js_graph["edges"].append({
            "from": edge['source'],
            "to": edge['target'],
            "color": "rgba(50, 121, 168)",
            "value": edge['props'][score_type],
            "label": F"{str(edge['props'][score_type])}\\n{', '.join(edge['props']['influence_areas'])}",
            "length": 250
        })

    return js_graph


@app.route('/')
def index():
    user_graphs = neo4j_users_db_connector.get_graphs()
    activity_graphs = neo4j_activities_db_connector.get_graphs()
    valid_graphs = []
    for graph in user_graphs:
        if graph in activity_graphs:
            valid_graphs.append(graph)
    valid_graphs = sorted(valid_graphs, key=lambda graph: (
        graph['network'], graph['date']))
    return render_template("index.html", graphs=valid_graphs)


# Example - GUI: http://localhost:5000/user_graph?graph=Test_2021-04-11&score_type=total&centrality=betweenness
# Example - JSON: http://localhost:5000/user_graph?graph=Test_2021-04-11&score_type=total&centrality=betweenness&format=json
@app.route('/user_graph')
def user_graph():
    data_format = request.args.get('format', None)
    score_type = request.args.get('score_type', 'total')
    centrality = request.args.get('centrality', 'degree')
    graph = request.args.get('graph', None).split("_")
    network_name, date = graph[0], graph[1]
    neo4j_graph, centralities_max = neo4j_users_db_connector.get_graph(
        network_name=network_name, date=date, relation_type="Influences")

    if len(neo4j_graph['nodes']) == 0 and len(neo4j_graph['links']) == 0:
        return F"Users Graph not found, make sure you use the correct network name and crawling date in the 'graph' url parameter"
    elif data_format == 'json':
        return jsonify(neo4j_graph)
    else:
        js_graph = constructJSGraph(
            neo4j_graph=neo4j_graph,
            graph_type="user_graph",
            score_type=score_type,
            centrality_max=centralities_max[centrality]
        )
    return render_template("graph.html", data=js_graph, graph_type="user_graph")


# Example - GUI: http://localhost:5000/path?graph=Test_2021-04-11&score_type=total&centrality=degree&source_name=mrsbayduck&target_name=EyeHamKnotYew
# Example - JSON: http://localhost:5000/path?graph=Test_2021-04-11&score_type=total&centrality=degree&source_name=mrsbayduck&target_name=EyeHamKnotYew&format=json
@ app.route('/path')
def path():
    data_format = request.args.get('format')
    graph = request.args.get('graph', None).split("_")
    network_name, date = graph[0], graph[1]
    centrality = request.args.get('centrality', 'degree')
    score_type = request.args.get('score_type', 'total')
    source_name = request.args.get('source_name', '')
    target_name = request.args.get('target_name', '')

    neo4j_graph, centralities_max = neo4j_users_db_connector.get_path(
        network_name=network_name,
        date=date,
        from_name=source_name,
        to_name=target_name
    )

    if len(neo4j_graph['nodes']) == 0 and len(neo4j_graph['links']) == 0:
        return F"No path is found between {source_name} and {target_name}"
    elif data_format == 'json':
        return jsonify(neo4j_graph)
    else:
        js_graph = constructJSGraph(
            neo4j_graph=neo4j_graph,
            graph_type="user_graph",
            score_type=score_type,
            centrality_max=centralities_max[centrality]
        )
    return render_template("graph.html", data=js_graph, graph_type="user_graph")


# Example - GUI: http://localhost:5000/score?graph=Test_2021-04-11&score_type=total&min_score=0&max_score=10&centrality=degree
# Example - JSON: http://localhost:5000/score?graph=Test_2021-04-11&score_type=total&min_score=0&max_score=10&centrality=degree&format=json
@ app.route('/score', methods=['GET'])
def score():
    data_format = request.args.get('format')
    graph = request.args.get('graph', None).split("_")
    network_name, date = graph[0], graph[1]
    min_score = int(request.args.get('min_score', 0))
    max_score = int(request.args.get('max_score', 0))
    score_type = request.args.get('score_type', 'total')
    centrality = request.args.get('centrality', 'degree')

    neo4j_graph, centralities_max = neo4j_users_db_connector.filter_by_score(
        network_name=network_name,
        date=date,
        score_type=score_type,
        lower_score=min_score,
        upper_score=max_score
    )

    if len(neo4j_graph['nodes']) == 0 and len(neo4j_graph['links']) == 0:
        return F"No edges having the score between {min_score} and {max_score} was found"
    elif data_format == 'json':
        return jsonify(neo4j_graph)
    else:
        js_graph = constructJSGraph(
            neo4j_graph=neo4j_graph,
            graph_type="user_graph",
            score_type=score_type,
            centrality_max=centralities_max[centrality]
        )
    return render_template("graph.html", data=js_graph, graph_type="user_graph")


# Example - GUI: http://localhost:5000/influence_area?graph=Test_2021-04-11&score_type=total&influence_areas=sport&influence_areas=entertainment&operation=OR&centrality=degree
# Example - JSON: http://localhost:5000/field?graph=Test_2021-04-11&score_type=total&influence_areas=sport&influence_areas=entertainment&operation=OR&centrality=degree&format=json
@ app.route('/influence_area', methods=['GET'])
def influence_area():
    graph = request.args.get('graph', None).split("_")
    network_name, date = graph[0], graph[1]
    score_type = request.args.get('score_type', 'total')
    influence_areas = request.args.to_dict(flat=False)

    if 'influence_areas' in influence_areas:
        influence_areas = influence_areas['influence_areas']
    operation = request.args.get('operation', 'OR')
    centrality = request.args.get('centrality', 'degree')
    data_format = request.args.get('format')

    neo4j_graph, centralities_max = neo4j_users_db_connector.filter_by_influence_area(
        network_name=network_name,
        date=date,
        areas_array=influence_areas,
        operation=operation
    )

    if len(neo4j_graph['nodes']) == 0 and len(neo4j_graph['links']) == 0:
        return F"No edges having the influence area(s) {influence_areas} was found using {operation} operation"
    elif data_format == 'json':
        return jsonify(neo4j_graph)
    else:
        js_graph = constructJSGraph(
            neo4j_graph=neo4j_graph,
            graph_type="user_graph",
            score_type=score_type,
            centrality_max=centralities_max[centrality]
        )
    return render_template("graph.html", data=js_graph, graph_type="user_graph")


# Example - GUI: http://localhost:5000/activity_graph?graph=Test_2021-04-11&score_type=total
# Example - JSON: http://localhost:5000/activity_graph?graph=Test_2021-04-11&score_type=total&format=json
@app.route('/activity_graph')
def activity_graph():
    graph = request.args.get('graph', None).split("_")
    network_name, date = graph[0], graph[1]
    score_type = request.args.get('score_type', "total")
    data_format = request.args.get('format', None)

    neo4j_graph, centralities_max = neo4j_activities_db_connector.get_graph(
        network_name=network_name, date=date, relation_type="Has")

    if len(neo4j_graph['nodes']) == 0 and len(neo4j_graph['links']) == 0:
        return "Activities Graph not found, make sure you use the correct network name and crawling date in the 'graph' url parameter"
    elif data_format == 'json':
        return jsonify(neo4j_graph)
    else:
        js_graph = constructJSGraph(
            neo4j_graph=neo4j_graph,
            graph_type="activity_graph",
            score_type=score_type,
            centrality_max=None
        )
    return render_template("graph.html", data=js_graph, graph_type="activity_graph")


@app.route('/statistics')
def statistics():
    statistic_measure = request.args.get('statistic_measure', None)
    submissions_type = request.args.get('submissions_type', 'Rising')
    graph = request.args.get('graph', None).split("_")
    network_name, date = graph[0], graph[1]
    score_type = request.args.get('score_type', "total")

    plt_img_path = F"statistics_plots/{statistic_measure}/{network_name}/{date}/"
    if statistic_measure == "crawling":
        plt_img_path += F"bar_plot_{submissions_type}.jpg"
    elif statistic_measure == "influence_areas_and_subreddits":
        plt_img_path += F"pie_plot_{submissions_type}.jpg"
    elif statistic_measure == "influence_scores":
        plt_img_path += F"box_plot_{score_type}.jpg"
    else:
        return "Unknown type of statistics, parameters might be missing"

    if os.path.isfile(plt_img_path):
        return send_file(plt_img_path, mimetype="image/jpg")
    else:
        return "Statistics from this network and date is not available, make sure you are using the correct network, submission type, date and score"


if __name__ == '__main__':
    app.run()
