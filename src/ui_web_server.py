from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from flask import Flask, jsonify, render_template, request, send_file
from classes.modelling.TextClassification import TextClassifier
from classes.caching.CacheHandler import CacheHandler
from flask_caching import Cache
from dotenv import load_dotenv
import time
import os

load_dotenv()

app = Flask(__name__)

if os.environ.get('CACHE_ON') == "True":
    cache_type = 'FileSystemCache'
else:
    cache_type = 'NullCache'

cache_timeout = int(os.environ.get('CACHE_TIMEOUT'))
config = {
    'CACHE_TYPE': cache_type,
    'CACHE_DIR': 'cache',
    "CACHE_DEFAULT_TIMEOUT": cache_timeout
}
# tell Flask to use the above defined config
app.config.from_mapping(config)
cache = Cache(app)


def get_host(target):
    """ Gets the hostname based on the configured environment. """
    if os.environ.get('IS_DOCKER') == "True":
        return "host.docker.internal"
    return os.environ.get(target)


""" Check of all required services is up an running before running this web server application, or wait """
number_of_connection_tries = 0
stop_trying = False  # Are all database services up and running?
while (not stop_trying):
    try:
        # Mongo DB connector
        mongo_db_connector = MongoDBConnector(
            host=get_host('mongo_db_host'),
            port=int(os.environ.get('mongo_db_port')),
            user=os.environ.get('mongo_db_user'),
            passowrd=os.environ.get('mongo_db_pass')
        )

        # Neo4j users database connector
        neo4j_users_db_connector = GraphDBConnector(
            host=get_host('neo4j_users_db_host'),
            port=int(os.environ.get('neo4j_users_db_port')),
            user=os.environ.get('neo4j_users_db_user'),
            password=os.environ.get('neo4j_users_db_pass')
        )

        # Neo4j activity database connector
        neo4j_activities_db_connector = GraphDBConnector(
            host=get_host('neo4j_activities_db_host'),
            port=int(os.environ.get('neo4j_activities_db_port')),
            user=os.environ.get('neo4j_activities_db_user'),
            password=os.environ.get('neo4j_activities_db_pass')
        )

        stop_trying = True

    except Exception as e:
        print("Waiting for database services ...")
        time.sleep(1)
        number_of_connection_tries += 1
        # change this value below if you want the application to wait more than 15 minutes (= 900 seconds)
        if number_of_connection_tries > 900:
            stop_trying = True


def constructJSGraph(neo4j_graph, graph_type, score_type, centrality_max, centrality):
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
            js_node["value"] = node['props'][centrality]
            js_node["color"] = {
                "background": F"rgba(240, 52, 52, {node['props'][centrality]/centrality_max})"}
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
@cache.cached(timeout=cache_timeout)
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


@app.route('/user_graph')
@cache.cached(timeout=cache_timeout, query_string=True)
def user_graph():
    data_format = request.args.get('format', None)
    score_type = request.args.get('score_type', 'total')
    centrality = request.args.get('centrality', 'degree')
    graph = request.args.get('graph', None).split(",")
    network_name, submissions_type, date = graph[0], graph[1], graph[2]
    neo4j_graph, centralities_max = neo4j_users_db_connector.get_graph(
        network_name=network_name, submissions_type=submissions_type, date=date, relation_type="Influences")

    if len(neo4j_graph['nodes']) == 0 and len(neo4j_graph['links']) == 0:
        return F"Users Graph not found, make sure you use the correct network name and crawling date in the 'graph' url parameter"
    elif data_format == 'json':
        return jsonify(neo4j_graph)
    else:
        js_graph = constructJSGraph(
            neo4j_graph=neo4j_graph,
            graph_type="user_graph",
            score_type=score_type,
            centrality_max=centralities_max[centrality],
            centrality=centrality
        )
    return render_template("graph.html", data=js_graph, graph_type="user_graph")


@ app.route('/path')
def path():
    data_format = request.args.get('format')
    graph = request.args.get('graph', None).split(",")
    network_name, submissions_type, date = graph[0], graph[1], graph[2]
    centrality = request.args.get('centrality', 'degree')
    score_type = request.args.get('score_type', 'total')
    source_name = request.args.get('source_name', '')
    target_name = request.args.get('target_name', '')

    neo4j_graph, centralities_max = neo4j_users_db_connector.get_path(
        network_name=network_name,
        submissions_type=submissions_type,
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
            centrality_max=centralities_max[centrality],
            centrality=centrality
        )
    return render_template("graph.html", data=js_graph, graph_type="user_graph")


@ app.route('/score', methods=['GET'])
def score():
    data_format = request.args.get('format')
    graph = request.args.get('graph', None).split(",")
    network_name, submissions_type, date = graph[0], graph[1], graph[2]
    min_score = int(request.args.get('min_score', 0))
    max_score = int(request.args.get('max_score', 0))
    score_type = request.args.get('score_type', 'total')
    centrality = request.args.get('centrality', 'degree')

    neo4j_graph, centralities_max = neo4j_users_db_connector.filter_by_score(
        network_name=network_name,
        submissions_type=submissions_type,
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
            centrality_max=centralities_max[centrality],
            centrality=centrality
        )
    return render_template("graph.html", data=js_graph, graph_type="user_graph")


@ app.route('/influence_area', methods=['GET'])
def influence_area():
    graph = request.args.get('graph', None).split(",")
    network_name, submissions_type, date = graph[0], graph[1], graph[2]
    score_type = request.args.get('score_type', 'total')
    influence_areas = request.args.to_dict(flat=False)

    if 'influence_areas' in influence_areas:
        influence_areas = influence_areas['influence_areas']
    operation = request.args.get('operation', 'OR')
    centrality = request.args.get('centrality', 'degree')
    data_format = request.args.get('format')

    neo4j_graph, centralities_max = neo4j_users_db_connector.filter_by_influence_area(
        network_name=network_name,
        submissions_type=submissions_type,
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
            centrality_max=centralities_max[centrality],
            centrality=centrality
        )
    return render_template("graph.html", data=js_graph, graph_type="user_graph")


@app.route('/activity_graph')
@cache.cached(timeout=cache_timeout, query_string=True)
def activity_graph():
    graph = request.args.get('graph', None).split(",")
    network_name, submissions_type, date = graph[0], graph[1], graph[2]
    score_type = request.args.get('score_type', "total")
    data_format = request.args.get('format', None)

    neo4j_graph, centralities_max = neo4j_activities_db_connector.get_graph(
        network_name=network_name, submissions_type=submissions_type, date=date, relation_type="Has")

    if len(neo4j_graph['nodes']) == 0 and len(neo4j_graph['links']) == 0:
        return "Activities Graph not found, make sure you use the correct network name and crawling date in the 'graph' url parameter"
    elif data_format == 'json':
        return jsonify(neo4j_graph)
    else:
        js_graph = constructJSGraph(
            neo4j_graph=neo4j_graph,
            graph_type="activity_graph",
            score_type=score_type,
            centrality_max=None,
            centrality=None
        )
    return render_template("graph.html", data=js_graph, graph_type="activity_graph")


@app.route('/statistics')
def statistics():
    statistic_measure = request.args.get('statistic_measure', None)
    graph = request.args.get('graph', None).split(",")
    network_name, submissions_type, date = graph[0], graph[1], graph[2]
    score_type = request.args.get('score_type', "total")

    plt_img_path = F"statistics_plots/{statistic_measure}/{network_name}/{date}/{submissions_type}/"
    if statistic_measure == "crawling":
        plt_img_path += F"crawling_bar_plot.jpg"
    elif statistic_measure == "influence_areas_and_subreddits":
        plt_img_path += F"topics_and_subreddits_pie_plot.jpg"
    elif statistic_measure == "influence_scores":
        plt_img_path += F"scores_box_plot_{score_type}.jpg"
    else:
        return "Unknown type of statistics, parameters might be missing"

    if os.path.isfile(plt_img_path):
        return send_file(plt_img_path, mimetype="image/jpg")
    else:
        return "Statistics from this network and date is not available, make sure you are using the correct network, submission type, date and score"


@app.route('/centrality_report')
@cache.cached(timeout=cache_timeout, query_string=True)
def centrality_report():
    graph = request.args.get('graph', None).split(",")
    data_format = request.args.get('format', None)
    network_name, submissions_type, date = graph[0], graph[1], graph[2]

    neo4j_graph, centralities_max = neo4j_users_db_connector.get_graph(
        network_name=network_name, submissions_type=submissions_type, date=date, relation_type="Influences")

    if len(neo4j_graph['nodes']) == 0 and len(neo4j_graph['links']) == 0:
        return "Activities Graph not found, make sure you use the correct network name and crawling date in the 'graph' url parameter"

    user_centrality_report = {
        "degree_centrality": {},
        "betweenness_centrality": {},
        "hits_centrality_auth":  {},
        "hits_centrality_hub":  {}
    }

    measured_centralities = {
        "degree_centrality": [],
        "betweenness_centrality": [],
        "hits_centrality_auth":  [],
        "hits_centrality_hub":  []
    }

    for measure, _ in user_centrality_report.items():
        for user_node in neo4j_graph["nodes"]:
            user_centrality_report[measure][user_node["props"]
                                            ["name"]] = user_node["props"][measure]
        measured_centralities[measure] = sorted(list(
            set(user_centrality_report[measure].values())), reverse=True)

    for measure, _ in user_centrality_report.items():
        user_centrality_report[measure] = sorted(
            user_centrality_report[measure].items(), key=lambda n: n[1], reverse=True)

    centrality = {
        "user_centrality_report": user_centrality_report,
        "measured_centralities": measured_centralities
    }

    if data_format == 'json':
        return jsonify(centrality)
    return render_template("centrality_report.html", centrality=centrality)


@app.route('/topic_detection_model')
@cache.cached(timeout=cache_timeout, query_string=True)
def topic_detection_model():
    graph = request.args.get('graph', None).split(",")
    data_format = request.args.get('format', None)
    network_name, submissions_type, date = graph[0], graph[1], graph[2]

    text_classifier = TextClassifier(
        mongo_db_connector, network_name, submissions_type, date)
    model_status = text_classifier.prepare_model()
    if model_status == "data not found":
        return F"data not found, the specified '{request.args.get('graph', None)}' graph is not found"
    evaluation_result = text_classifier.evaluate_model()
    classification_report, confusion_matrix, labels = text_classifier.get_report()
    tunning_results = text_classifier.tune_model()
    result = {
        "labels": labels,
        "evaluation": evaluation_result,
        "classification_report": classification_report,
        "confusion_matrix": confusion_matrix.tolist(),
        "tunning": tunning_results
    }
    if data_format == 'json':
        return jsonify(result)
    return render_template("topic_detection_model.html", result=result)


@app.route('/clear_cache')
def clear_cache():
    secret_key = request.args.get('key', None)

    if secret_key == os.environ.get('CACHE_SECRET_PASSWORD'):
        cache.init_app(app, config=config)

        with app.app_context():
            result = cache.clear()

        if result:
            return "Cache successfully cleared."
        return "Not able to clear cache."
    else:
        return "Access denied."


@app.route('/clear_and_refresh_cache')
def clear_and_refresh_cache():
    secret_key = request.args.get('key', None)

    if secret_key == os.environ.get('CACHE_SECRET_PASSWORD'):
        domain_name = "http://localhost:5000"
        cache_directory_path = "cache"

        cache_handler = CacheHandler(domain_name, cache_directory_path,
                                     neo4j_users_db_connector, neo4j_activities_db_connector)

        cache_handler.clear_cache()

        cache_handler.fetchIndexPage()

        cache_handler.fetchUserGraphs()

        cache_handler.fetchActivityGraphs()

        cache_handler.fetchCentralityReports()

        cache_handler.fetchTopicDetectionModel()

        return "Cache successfully refreshed."
    else:
        return "Access denied."


if __name__ == '__main__':
    app.run(host='0.0.0.0')
