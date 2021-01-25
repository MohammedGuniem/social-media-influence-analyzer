from Neo4jConnector import Neo4jConnector
from GraphModelling import GraphModel
from dotenv import load_dotenv
import os

load_dotenv()

MongoDB_connection_string = os.environ.get('mongo_connnection_string')

graph_model = GraphModel("Model A", MongoDB_connection_string)

model = graph_model.buildModel("Home")

neo4j_connector = Neo4jConnector(
    "bolt://localhost:7687", "neo4j", "1234")

for relation_id, relation_node in model.items():
    neo4j_connector.create_pair(relation_node["FROM"]["type"], relation_node["FROM"]["id"], relation_node["FROM"]["data"],
                                relation_node["RELATIONSHIP"]["type"], relation_id, relation_node["RELATIONSHIP"]["data"],
                                relation_node["TO"]["type"], relation_node["TO"]["id"], relation_node["TO"]["data"])

neo4j_connector.close()
