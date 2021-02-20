from classes.statistics.Statistics import Statistics as statistics_methods
from classes.modelling.ActionGraphModelling import ActionGraphModel
from dotenv import load_dotenv
import os

# Loading Enviroment variables and initiating a action graph model instance
load_dotenv()
action_graph_model = ActionGraphModel(
    mongodb_connection_string=os.environ.get('mongo_connnection_string'),
    neo4j_connection_string=os.environ.get('neo4j_connection_string'),
    neo4j_username=os.environ.get('neo4j_username'),
    neo4j_password=os.environ.get('neo4j_password'),
    construct_neo4j_graph=False
)
action_graph_model.build_model(
    subreddit_display_name="wallstreetbets",
    submission_type="Rising"
)

action_model_edge_weights = {
    'Action Model': action_graph_model.edges.values()
}
action_model_statistics = statistics_methods.getSummaryStatistics(
    action_model_edge_weights)
print(action_model_statistics)
