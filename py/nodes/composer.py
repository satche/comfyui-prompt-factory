# from ..utils.config import load_nodes_config
import numpy as np

from ..utils.config import load_nodes_config
from .node_factory import NodeFactory
from .node_factory._tags import select_tags


class Composer:
    """
    A ComfyUI node to compose prompt with variables.
    Inputs: string with {variables}
    Output: prompt composed with variables
    """
    
    def __init__(self):
        self.data = load_nodes_config()

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    FUNCTION = "build_prompt"
    CATEGORY = "⚙️ Prompt Factory/✒️ Composer"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff
                }),
                "prompt": ("STRING", {"default": "", "multiline": True})
            },
            "optional": {
            }
        }

    def build_prompt(self, **args):
        """
        Build the prompt according to the node inputs
        Concatenate the tags and return the prompt
        """
        rng = np.random.default_rng(args["seed"])
        variables = {}        
        tags = {}

        # Replace tags with corresponding variables
        for key, value in self.data.items():
            if "variables" in self.data[key]:
                for v_key, v_value in self.data[key]["variables"].items():
                    variables[v_key] = select_tags(rng, v_value)
                tags = NodeFactory.apply_variables(tags, variables)
            
            if "tags" in self.data[key]:
                for key, value in self.data[key]["tags"].items():
                    tags[key] = select_tags(rng, value, p=1)
                    
                    """
                    if isinstance(value, dict) and value not in RESERVED_KEYS:
                        for sub_key, sub_value in value.items():
                            tags[sub_key] = select_tags(rng, sub_value, p=1)
                    """

        variables = {**tags, **variables}
        prompt = args["prompt"]
        prompt = NodeFactory.apply_variables(prompt, variables)
        
        return (prompt,)