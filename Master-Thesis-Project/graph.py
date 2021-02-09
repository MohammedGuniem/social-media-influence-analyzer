from classes.database_connectors.Neo4jConnector import Graph

graph_instance = Graph("bolt://localhost:7687", "neo4j", "1234")

graph_instance.addNode(ID="111", Type="Person", props={"name": "Node 1"})
graph_instance.addNode(ID="222", Type="Person", props={"name": "Node 2"})

graph_instance.addNode(ID="333", Type="Person", props={"name": "Node 3"})

graph_instance.addEdge(relation_Type="INFLUENCES", relation_props={
                       "weight": 101}, from_ID="111", from_Type="Person", to_ID="333", to_Type="Person")
