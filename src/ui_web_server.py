from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.database_connectors.Neo4jConnector import GraphDBConnector
from flask import Flask, jsonify, abort, render_template, request, send_file
from classes.modelling.TextClassification import TextClassifier
from classes.caching.CacheHandler import CacheHandler
from classes.logging.LoggHandler import LoggHandler
from flask_httpauth import HTTPDigestAuth
from flask_caching import Cache
from dotenv import load_dotenv
from datetime import date
import time
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Setting up caching
if os.environ.get('CACHE_ON') == "True":
    cache_type = 'FileSystemCache'  # cache records stored on file system
else:
    cache_type = 'NullCache'  # no cache

cache_timeout = int(os.environ.get('CACHE_TIMEOUT'))
config = {
    'CACHE_TYPE': cache_type,
    'CACHE_DIR': os.environ.get('CACHE_DIR_PATH'),
    "CACHE_DEFAULT_TIMEOUT": cache_timeout
}
app.config.from_mapping(config)
cache = Cache(app)

# Setting up HTTP Digest Auth
auth = HTTPDigestAuth()
usernames = os.environ.get('ADMIN_USERNAMES').split(",")
passwords = os.environ.get('ADMIN_PASSWORDS').split(",")
users = {}
if len(usernames) == len(passwords):
    for user in usernames:
        users[user] = passwords[usernames.index(user)]


@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None


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
            passowrd=os.environ.get('mongo_db_pass'),
            access_mode="ReadOnly"
        )

        # Neo4j users database connector
        neo4j_db_users_connector = GraphDBConnector(
            host=get_host('neo4j_users_db_host'),
            port=int(os.environ.get('neo4j_users_db_port')),
            user=os.environ.get('neo4j_users_db_user'),
            password=os.environ.get('neo4j_users_db_pass'),
            access_mode="ReadOnly"
        )

        # Neo4j activity database connector
        neo4j_db_activities_connector = GraphDBConnector(
            host=get_host('neo4j_activities_db_host'),
            port=int(os.environ.get('neo4j_activities_db_port')),
            user=os.environ.get('neo4j_activities_db_user'),
            password=os.environ.get('neo4j_activities_db_pass'),
            access_mode="ReadOnly"
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
            if centrality_max == 0:
                trans = 1
            else:
                trans = node['props'][centrality]/centrality_max
            js_node["color"] = {
                "background": F"rgba(240, 52, 52, {trans})"}
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


@app.errorhandler(404)
def errorhandler(e):
    today_date = date.today()
    str_date = str(today_date)
    logg_handler = LoggHandler(str_date)
    logg_handler.logg_ui_error(e)
    return F"This error has occured: <br /><br />{e}<br /><br />Contact your administrator to check the UI_Web_Server logging directory of this day {str_date}"


@app.route('/')
@cache.cached(timeout=cache_timeout, query_string=True)
def index():
    try:
        user_graphs = neo4j_db_users_connector.get_graphs()
        activity_graphs = neo4j_db_activities_connector.get_graphs()
        networks, submissions_types, crawling_dates = [], [], []
        for graph in user_graphs:
            if graph in user_graphs and graph in activity_graphs:
                networks.append(graph['network'])
                submissions_types.append(graph['submissions_type'])
                crawling_dates.append(graph['date'])
        return render_template("index.html", networks=sorted(networks, reverse=True), submissions_types=submissions_types, crawling_dates=sorted(crawling_dates))
    except Exception as e:
        abort(404, description=e)


@ app.route('/influence_graph')
@ cache.cached(timeout=cache_timeout, query_string=True)
def influence_graph():
    try:
        data_format = request.args.get('format', None)
        score_type = request.args.get('score_type', 'total')
        centrality = request.args.get('centrality', 'degree')
        network_name = request.args.get('network_name', None)
        submissions_type = request.args.get('submissions_type', None)
        date = request.args.get('crawling_date', None)

        neo4j_graph, centralities_max = neo4j_db_users_connector.get_graph(
            network_name=network_name, submissions_type=submissions_type, date=date, relation_type="Influences")

        if len(neo4j_graph['nodes']) == 0 and len(neo4j_graph['links']) == 0:
            return render_template(
                "not_found.html",
                message={
                    "header": "Influence Graph not found",
                    "body": "Make sure you use the correct combination of network- and group- name, along with the crawling date in the graph identifying URL parameter"
                })
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
    except Exception as e:
        abort(404, description=e)


@ app.route('/path')
def path():
    try:
        data_format = request.args.get('format')
        network_name = request.args.get('network_name', None)
        submissions_type = request.args.get('submissions_type', None)
        date = request.args.get('crawling_date', None)
        centrality = request.args.get('centrality', 'degree')
        score_type = request.args.get('score_type', 'total')
        source_name = request.args.get('source_name', '')
        target_name = request.args.get('target_name', '')

        neo4j_graph, centralities_max = neo4j_db_users_connector.get_path(
            network_name=network_name,
            submissions_type=submissions_type,
            date=date,
            from_name=source_name,
            to_name=target_name
        )

        if len(neo4j_graph['nodes']) == 0 and len(neo4j_graph['links']) == 0:
            return render_template(
                "not_found.html",
                message={
                    "header": "No path is found",
                    "body": F"No path is found between {source_name} and {target_name} in the specified influence graph"
                })
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
    except Exception as e:
        abort(404, description=e)


@ app.route('/score', methods=['GET'])
def score():
    try:
        data_format = request.args.get('format')
        network_name = request.args.get('network_name', None)
        submissions_type = request.args.get('submissions_type', None)
        date = request.args.get('crawling_date', None)
        min_score = int(request.args.get('min_score', 0))
        max_score = int(request.args.get('max_score', 0))
        score_type = request.args.get('score_type', 'total')
        centrality = request.args.get('centrality', 'degree')

        neo4j_graph, centralities_max = neo4j_db_users_connector.filter_by_score(
            network_name=network_name,
            submissions_type=submissions_type,
            date=date,
            score_type=score_type,
            lower_score=min_score,
            upper_score=max_score
        )

        if len(neo4j_graph['nodes']) == 0 and len(neo4j_graph['links']) == 0:
            return render_template(
                "not_found.html",
                message={
                    "header": "Score range does not contain any edges",
                    "body": F"No edges having the score between {min_score} and {max_score} was found in the specified influence graph"
                })
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
    except Exception as e:
        abort(404, description=e)


@ app.route('/influence_area', methods=['GET'])
def influence_area():
    try:
        network_name = request.args.get('network_name', None)
        submissions_type = request.args.get('submissions_type', None)
        date = request.args.get('crawling_date', None)
        score_type = request.args.get('score_type', 'total')
        influence_areas = request.args.to_dict(flat=False)

        if 'influence_areas' in influence_areas:
            influence_areas = influence_areas['influence_areas']
        operation = request.args.get('operation', 'OR')
        centrality = request.args.get('centrality', 'degree')
        data_format = request.args.get('format')

        neo4j_graph, centralities_max = neo4j_db_users_connector.filter_by_influence_area(
            network_name=network_name,
            submissions_type=submissions_type,
            date=date,
            areas_array=influence_areas,
            operation=operation
        )

        if len(neo4j_graph['nodes']) == 0 and len(neo4j_graph['links']) == 0:
            return render_template(
                "not_found.html",
                message={
                    "header": "Specified influence field(s) not found",
                    "body": F"No edges having the influence area(s) {influence_areas} was found using {operation} operation"
                })
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
    except Exception as e:
        abort(404, description=e)


@ app.route('/centrality_report')
@ cache.cached(timeout=cache_timeout, query_string=True)
def centrality_report():
    try:
        data_format = request.args.get('format', None)
        network_name = request.args.get('network_name', None)
        submissions_type = request.args.get('submissions_type', None)
        date = request.args.get('crawling_date', None)

        neo4j_graph, centralities_max = neo4j_db_users_connector.get_graph(
            network_name=network_name, submissions_type=submissions_type, date=date, relation_type="Influences")

        if len(neo4j_graph['nodes']) == 0 and len(neo4j_graph['links']) == 0:
            return render_template(
                "not_found.html",
                message={
                    "header": "Influence Graph not found",
                    "body": "Make sure you use the correct combination of network- and group- name, along with the crawling date in the graph identifying URL parameter"
                })

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
        else:
            return render_template("centrality_report.html", centrality=centrality)
    except Exception as e:
        abort(404, description=e)


@ app.route('/activity_graph')
@ cache.cached(timeout=cache_timeout, query_string=True)
def activity_graph():
    try:
        network_name = request.args.get('network_name', None)
        submissions_type = request.args.get('submissions_type', None)
        date = request.args.get('crawling_date', None)
        score_type = request.args.get('score_type', "total")
        data_format = request.args.get('format', None)

        neo4j_graph, centralities_max = neo4j_db_activities_connector.get_graph(
            network_name=network_name, submissions_type=submissions_type, date=date, relation_type="Has")

        if len(neo4j_graph['nodes']) == 0 and len(neo4j_graph['links']) == 0:
            return render_template(
                "not_found.html",
                message={
                    "header": "Activity Graph not found",
                    "body": "Make sure you use the correct combination of network- and group- name, along with the crawling date in the graph identifying URL parameter"
                })
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
    except Exception as e:
        abort(404, description=e)


@ app.route('/statistics')
def statistics():
    try:
        statistic_measure = request.args.get('statistic_measure', None)
        network_name = request.args.get('network_name', None)
        submissions_type = request.args.get('submissions_type', None)
        date = request.args.get('crawling_date', None)
        score_type = request.args.get('statistic_score_type', "total")

        plt_img_path = F"statistics_plots/{statistic_measure}/{network_name}/{date}/{submissions_type}/"
        if statistic_measure == "crawling":
            plt_img_path += F"crawling_bar_plot.jpg"
        elif statistic_measure == "influence_areas_and_groups":
            plt_img_path += F"topics_and_subreddits_pie_plot.jpg"
        elif statistic_measure == "influence_scores":
            plt_img_path += F"scores_box_and_hist_plot_{score_type}.jpg"
        elif statistic_measure == "centrality":
            plt_img_path += F"centralitys_box_and_hist_plot.jpg"
        else:
            return "Unknown type of statistics, parameters might be missing"

        if os.path.isfile(plt_img_path):
            return send_file(plt_img_path, mimetype="image/jpg")
        else:
            return render_template(
                "not_found.html",
                message={
                    "header": "Statistics not found",
                    "body": "Make sure you use the correct combination of network- and group- name, along with the crawling date and plot type in the graph identifying URL parameter"
                })
    except Exception as e:
        abort(404, description=e)


@ app.route('/topic_detection_model')
@ cache.cached(timeout=cache_timeout, query_string=True)
def topic_detection_model():
    try:
        network_name = request.args.get('network_name', None)
        submissions_type = request.args.get('submissions_type', None)
        date = request.args.get('crawling_date', None)
        data_format = request.args.get('format', None)

        text_classifier = TextClassifier(
            mongo_db_connector, network_name, submissions_type, date)
        model_status = text_classifier.prepare_model()
        if model_status == "data not found":
            return render_template(
                "not_found.html",
                message={
                    "header": "Text Classification Report not found",
                    "body": F"The specified URL paramteres might not refer to any influence graph"
                })
        evaluation_result = text_classifier.initially_evaluate_non_tuned_model()
        classification_report, confusion_matrix, labels = text_classifier.finally_evaluate_tuned_model()
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
    except Exception as e:
        abort(404, description=e)


@ app.route('/clear_cache')
@ auth.login_required
def clear_cache():
    try:
        cache.init_app(app, config=config)
        with app.app_context():
            result = cache.clear()
        if result:
            return "Cache successfully cleared."
        return "Not able to clear cache."
    except Exception as e:
        abort(404, description=e)


@ app.route('/refresh_cache')
@ auth.login_required
def refresh_cache():
    try:
        network_name = request.args.get('network_name', None)
        submissions_type = request.args.get('submissions_type', None)
        date = request.args.get('crawling_date', None)

        cache_handler = CacheHandler(
            domain_name=os.environ.get('DOMAIN_NAME'),
            cache_directory_path=os.environ.get('CACHE_DIR_PATH'),
            network_name=network_name,
            submissions_type=submissions_type,
            crawling_date=date,
            output_msg=False
        )
        cache_handler.refresh_system_cache()

        return "Cache successfully refreshed."
    except Exception as e:
        abort(404, description=e)


if __name__ == '__main__':
    app.run(host=os.environ.get("HOST_IPv4"), port=int(os.environ.get("PORT")))
