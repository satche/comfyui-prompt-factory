import numpy as np

from ..utils.config import (
    load_nodes_config,
    load_variables_config,
    RESERVED_KEYS
)

from .node_factory._variables import process_variables, apply_variables
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
    CATEGORY = "⚙️ Prompt Factory/🛠️ Utils"

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
        Transform tags, subtags and variables as reusable {variables}
        Return the prompt with the variables replaced
        """
        rng = np.random.default_rng(args["seed"])
        
        # Extract global and local variables
        global_variables = load_variables_config()
        local_variables = self._extract_local_variables(rng, global_variables)
        variables = {**global_variables, **local_variables}

        # Also transforms tags as variables
        tags = self._extract_tags(rng)
        processed_tags = apply_variables(rng, tags, variables)
        
        # Process whole node to use as variable
        nodes = {}
        for key, value in self.data.items():
            nodes[key] = select_tags(rng, value)

        # Merge everything and replace in prompt
        variables = {**variables, **processed_tags, **nodes}        
        prompt = args["prompt"]
        prompt = apply_variables(rng, prompt, variables)

        return (prompt,)

    def _extract_local_variables(self, rng, global_variables):
        processed_variables = {}
        for key in self.data.keys():
            if "variables" in self.data[key]:
                local_variables = process_variables(
                    rng, self.data[key]["variables"])
                new_variable = apply_variables(
                    rng, local_variables, global_variables)
                processed_variables.update(new_variable)

        return processed_variables

    def _extract_tags(self, rng):
        tags = {}
        for key, value in self.data.items():
            if "tags" in self.data[key]:
                for tag_key, tag_value in self.data[key]["tags"].items():
                    tags[tag_key] = select_tags(rng, tag_value, p=1)
                    if isinstance(tag_value, dict) and \
                       tag_value not in RESERVED_KEYS:
                        self._process_sub_tags(rng, tags, tag_value)
        return tags

    def _process_sub_tags(self, rng, tags, sub_tags):
        for sub_key, sub_value in sub_tags.items():
            if sub_key not in RESERVED_KEYS:
                tags[sub_key] = select_tags(rng, sub_value, p=1)
                if isinstance(sub_value, dict):
                    self._process_sub_tags(rng, tags, sub_value)