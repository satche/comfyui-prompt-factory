import numpy as np

from ...utils.config import load_nodes_config
from ._inputs import build_inputs, apply_input_values
from ._tags import select_tags, stringify_tags


class NodeFactory:

    def __init__(self):
        config = load_nodes_config()
        self.data = config[self.__class__.__name__.lower()]

    @classmethod
    def INPUT_TYPES(cls):
        instance = cls()
        inputs = build_inputs(instance)
        inputs["required"]["seed"] = ("INT", {
            "default": 0,
            "min": 0,
            "max": 0xffffffffffffffff
        })
        return inputs

    RETURN_TYPES = ("STRING",)
    FUNCTION = "build_prompt"
    CATEGORY = "⚙️ Prompt Factory/⭐️ My Nodes"

    def build_prompt(self, **args):
        """
        Build the prompt according to the node inputs
        Concatenate the tags and return the prompt
        """
        rng = np.random.default_rng(args["seed"])

        # Build inputs
        input_values = apply_input_values(self.data["tags"], args)

        # Select tags
        tags = {}
        for key, value in input_values.items():
            tags[key] = select_tags(rng, value)

        # Replace tags with corresponding variables
        variables = {}
        if "variables" in self.data:
            for key, value in self.data["variables"].items():
                variables[key] = select_tags(rng, value)
            tags = self.apply_variables(tags, variables)

        # Build and clean-up final prompt
        prompt = stringify_tags(tags.values(), ", ")
        return (prompt,)

    @classmethod
    def create_node(cls, node_id, node_name=None):
        """
        Create a new node with ID and name
        """
        return type(node_id, (cls,), {
            "id": node_id,
            "name": node_name or node_id.capitalize()
        })

    @staticmethod
    def apply_variables(tags, variables):
        """
        Replace {tags} with corresponding variable
        """
        
        if isinstance(tags, str):
            for var_key, var_value in variables.items():
                tags = tags.replace("{"+var_key+"}", f"{var_value}")
            return [tags]
        
        for key, value in tags.items():
            for var_key, var_value in variables.items():
                value = value.replace("{"+var_key+"}", f"{var_value}")
            tags[key] = value
            
        return tags

    __all__ = ["NodeFactory"]
