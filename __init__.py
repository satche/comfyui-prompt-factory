from .py.utils import load_nodes_config
from .py.node import Node

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
config = load_nodes_config()

#  Create each node according to the config folder
for key, value in config.items():
    node_id = key
    node_name = value["name"]
    node_class = Node.create_node(node_id, node_name)
    NODE_CLASS_MAPPINGS[node_id] = node_class
    NODE_DISPLAY_NAME_MAPPINGS[node_id] = node_name

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
