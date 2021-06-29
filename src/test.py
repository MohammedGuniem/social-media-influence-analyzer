from classes.database_connectors.Neo4jConnector import GraphDBConnector
from dotenv import load_dotenv
import requests
import os

load_dotenv()

try:
    def get_host(target):
        """ Gets the hostname based on the configured environment. """
        if os.environ.get('IS_DOCKER') == "True":
            return "host.docker.internal"
        return os.environ.get(target)

    # Neo4j users database connector
    neo4j_users_db_connector = GraphDBConnector(
        host=get_host('neo4j_users_db_host'),
        port=int(os.environ.get('neo4j_users_db_port')),
        user=os.environ.get('neo4j_users_db_user'),
        password=os.environ.get('neo4j_users_db_pass')
    )
    user_graphs = neo4j_users_db_connector.get_graphs()
    print(user_graphs)
    for graph in user_graphs:
        url = F"http://localhost:5000/topic_detection_model?graph={graph['network']},{graph['submissions_type']},{graph['date']}"
        x = requests.get(url)
        print(x.status_code)

except:
    print("failed")
