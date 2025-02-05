import argparse
from py.utils import load_nodes_config
from py.node import Node

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
config = load_nodes_config()

#  Create each node according to the config folder
for key, value in config.items():
    node_id = key
    node_name = value.get("name", key)
    node_class = Node.create_node(node_id, node_name)
    NODE_CLASS_MAPPINGS[node_id] = node_class
    NODE_DISPLAY_NAME_MAPPINGS[node_id] = node_name

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

#  Create each node according to the config folder


def main(seed):
    config_args = {
        "seed": seed,
    }

    print(f"SEED: {seed}")

    for key in config.keys():
        node_class = NODE_CLASS_MAPPINGS[key]
        node = node_class()

        inputs = node.INPUT_TYPES()
        node_name = inputs["required"]["name"][1]["default"]
        required_keys = [k for k in inputs.get("required", []) if k != "name"]

        print("---")
        print(node_name)
        print("inputs:", required_keys)
        print("prompt:", node.build_prompt(**config_args))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process some integers.")

    parser.add_argument(
        '-s', '--seed',
        type=int,
        default=1,
        help='Seed value'
    )

    args = parser.parse_args()

    main(args.seed)
