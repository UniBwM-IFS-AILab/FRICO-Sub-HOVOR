from hovor.configuration.json_configuration_provider import JsonConfigurationProvider
import jsonpickle
from pathlib import Path
from ipysigma import Sigma
import networkx as nx
from pyvis import network as net 

class Node: 
    def __init__(self, action_name, is_goal, is_initial, node_id) -> None:
        self.action_name = action_name
        self.is_goal = is_goal 
        self.is_initial = is_initial
        self.node_id = node_id
        self.group =  self._group()

    
    def _group(self): 
        if self.is_goal: 
            return  "goal"
        
        if self.is_initial: 
            return "initial"
        
        return "convo"
            
    
    def __repr__(self) -> str:
        return f"(action name: {self.action_name}, is_goal: {self.is_goal}, is_initial: {self.is_initial}, node_id: {self.node_id} )"



output_files_path = "/home/qnc/Plan4Dial/plan4dial/plan4dial/local_data/conversation_alignment_bots/ijcai_bot/output_files"
configuration_provider = JsonConfigurationProvider(str(Path(output_files_path) / "data"))
json = jsonpickle.encode(configuration_provider)
configuration_provider = jsonpickle.decode(json)
# configuration_provider.check_all_action_builders()

plan = configuration_provider.plan


        
nodes = []
node_id_index = {}
for n in plan.nodes: 
    nodes.append(Node(n.action_name, n.is_goal, n.is_initial, n.node_id))
    node_id_index[n.node_id] = len(nodes)-1
print(nodes)

edges = []
for e in plan.edges: 
    source = e.src.node_id
    dest = e.dst.node_id
    edges.append((source, dest))
    


G = nx.Graph()
is_goal = {node.node_id: node.is_goal for node in nodes}
is_initial = {node.node_id: node.is_initial for node in nodes}
action_name = {node.node_id: node.action_name for node in nodes}
labels = {node.node_id:node.group for node in nodes}
G.add_nodes_from([n.node_id for n in nodes])
nx.set_node_attributes(G,action_name, "label")
nx.set_node_attributes(G,is_goal, "is_goal")
nx.set_node_attributes(G,labels,"group" )
nx.set_node_attributes(G,is_initial, "is_initial")
G.add_edges_from(edges)



g = net.Network(notebook=True,cdn_resources='in_line')

g.from_nx(G)
g.show_buttons(filter_=['nodes','physics'])
g.show('/home/qnc/Downloads/output.html')