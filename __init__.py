from .py.utils import load_config
from .py.node import Node

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
data = load_config()

for key, value in data.items():
    node_id = key
    node_name = value["name"]
    node_class = Node.create_node(node_id, node_name)
    NODE_CLASS_MAPPINGS[node_id] = node_class
    NODE_DISPLAY_NAME_MAPPINGS[node_id] = node_name

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
