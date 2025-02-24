import argparse
from py.nodes.node_factory import NodeFactory
from py.utils.config import load_nodes_config

config = load_nodes_config()


def main(seed, with_inputs):

    print(f"SEED: {seed}")
    print("---")

    # Create prompt for each node
    for key, value in config.items():
        ClassNode = NodeFactory.create_node(key)
        node = ClassNode()
        
        node_name = value.get("name", key)
        inputs = node.INPUT_TYPES()["required"]
        if "seed" in inputs:
            del inputs["seed"]
        prompt = node.build_prompt(seed=seed)

        print(f"{node_name:<20} {prompt[0]}")

        # Optionally display inputs
        if with_inputs:
            for sub_key, sub_value in inputs.items():
                if isinstance(sub_value[0], list):
                    sub_value = sub_value[0]
                elif isinstance(sub_value[0], str):
                    sub_value = sub_value[1]["default"]
                    if sub_value is True:
                        sub_value = "Boolean"
                print(f"> {sub_key:<20} {sub_value}")
            print("---")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Generate a prompt from a node."
    )

    parser.add_argument(
        "-s", "--seed",
        type=int,
        default=0,
        help="Seed value for random number generator"
    )

    parser.add_argument(
        "-i", "--inputs",
        action="store_true",
        help="Display inputs for each node"
    )

    args = parser.parse_args()
    main(seed=args.seed, with_inputs=args.inputs)
