from .py.utils.config import load_nodes_config
from .node_factory import NodeFactory
from .py.nodes.merge_strings import MergeStrings

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
WEB_DIRECTORY = "./web"

# Create each node according to the config folder
config = load_nodes_config()

for key, value in config.items():
    node_id = key
    node_name = value.get("name", key)
    ClassNode = NodeFactory.create_node(node_id, node_name)
    NODE_CLASS_MAPPINGS[node_id] = ClassNode
    NODE_DISPLAY_NAME_MAPPINGS[node_id] = node_name

# Add additional nodes
NODE_CLASS_MAPPINGS["MergeStrings"] = MergeStrings
NODE_DISPLAY_NAME_MAPPINGS["MergeStrings"] = "🪡 Merge Strings"

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY"
]
