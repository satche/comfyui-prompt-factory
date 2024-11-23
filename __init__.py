from .utils import load_config
from .node import Node


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
data = load_config()


# Dynamically create node classes according to the config file
class NodeFactory:
    pass


for key, value in data.items():
    node_id = key
    node_name = value["name"] or key.capitalize()
    setattr(
        NodeFactory,
        node_id,
        type(node_id, (Node,), {
            "id": node_id,
            "name": node_name
        }),
    )

for key in data.keys():
    node = getattr(NodeFactory, key)
    NODE_CLASS_MAPPINGS[node.id] = node
    NODE_DISPLAY_NAME_MAPPINGS[node.id] = node.name

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
