import fnmatch
import dpath
import numpy as np

from py.utils.config import load_rules, load_nodes_config
from py.nodes.node_factory._tags import select_tags


class ApplyRules:
    """
    A ComfyUI node to apply rules to a string.
    Input: string
    Output: filtered string
    """
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    FUNCTION = "apply_rules"
    CATEGORY = "⚙️ Prompt Factory/🛠️ Utils"

    def __init__(self):
        self.config = load_nodes_config()
        self.rules = load_rules()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "rules": (["all", *cls.rules.keys()]),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff
                }),
            },
            "optional": {}
        }

    def apply_rules(self, prompt, rule, seed):
        """
        Apply the rules defined in config file.
        Add and remove tags in the prompt
        according to others tags in the same prompt
        """
        rng = np.random.default_rng(seed)
        tags = prompt.split(", ")

        # Merge all the rule together
        if rule == "all":
            merged_rules = {}
            for r_name, r_list in self.rules.items():
                for r in r_list:
                    for key, value in r.items():
                        if key not in merged_rules:
                            merged_rules[key] = []
                        if isinstance(value, list):
                            merged_rules[key].extend(value)
                        else:
                            merged_rules[key].append(value)
            self.rules["all"] = [merged_rules]

        # Apply the rules
        for r in self.rules[rule]:
            triggers = r["triggers"]
            actions = r["actions"]
            p = r.get("probability", 1)

            if rng.random() > p:
                continue

            # If any triggering tag occurs in the prompt,
            # run all the defined actions
            for trigger in triggers:
                if fnmatch.fnmatch(prompt, trigger):
                    tags = run_actions(rng, actions, tags, self.config)
                    break

        return tags


def run_actions(rng, actions, tags, config):
    """
    Run actions from the rule.
    Add or remove tags with filtering tags
    """

    process_tags = tags.copy()

    for action in actions:

        type = action.get("type", "add")
        value = action.get("value", [])
        p = action.get("probability", 1)

        if rng.random() > p:
            continue

        filtering_tags = process_action_value(value, config)

        match type:

            case "add":
                value = select_tags(rng, filtering_tags)
                process_tags.append(value)

            case "remove":

                # filter: remove tags that match any "remove" value
                process_tags = [tag for tag in process_tags
                                if not any(
                                    fnmatch.fnmatch(tag, f"*{v}*")
                                    for v in filtering_tags
                                )]

    return process_tags


def process_action_value(value, config):
    """
    Process the action's value.
    Return selected tags randomly or according to a given path
    """

    tags = []

    if isinstance(value, str):
        value = [value]

    # If the value is a path,
    # take all the tags from this path
    for v in value:
        if is_path(v):
            for k, i in dpath.search(config, v,
                                     yielded=True, dirs=False):
                if isinstance(i, str):
                    tags.append(i)
        else:
            tags.append(v)

    return tags


def is_path(string):
    "Check if the value is a glob path"
    is_path = isinstance(string, str) and ("/" in string or "*" in string)
    return is_path
