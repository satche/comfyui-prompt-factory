import numpy as np

from ..utils.config import load_nodes_config, RESERVED_KEYS
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
        variables = self._extract_variables(rng)
        tags = self._extract_tags(rng)

        variables = {**tags, **variables}
        prompt = args["prompt"]
        prompt = NodeFactory.apply_variables(prompt, variables)

        return (prompt,)

    def _extract_variables(self, rng):
        variables = {}
        for key, value in self.data.items():
            if "variables" in self.data[key]:
                for v_key, v_value in self.data[key]["variables"].items():
                    variables[v_key] = select_tags(rng, v_value)
        return variables

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