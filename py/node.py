import numpy as np
import dpath
from .utils import load_nodes_config


class Node:

    def __init__(self):
        config = load_nodes_config()
        self.data = config[self.__class__.__name__.lower()]

    @classmethod
    def INPUT_TYPES(cls):
        inputs = cls().build_inputs()
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
        Build the prompt according to the node's inputs
        Concatenate the tags and return the prompt
        """
        rng = np.random.default_rng(args["seed"])
        input_values = self.apply_input_values(self.data["tags"], args)

        tags = {}
        for key, value in input_values.items():
            tags[key] = self.select_tags(rng, value)

        prompt = self.stringify_tags(tags.values())
        return (prompt,)

    def apply_input_values(self, data, inputs):
        """
        Apply node's selected inputs value to the tags
        Can be the selected value, a random one or none
        """
        applied_values = {}

        def traverse(data):

            for key, value in data.items():
                selected = inputs.get(key, "random")

                match selected:
                    case "none":
                        continue

                    case "random":

                        if isinstance(value, str):
                            applied_values[key] = value

                        if isinstance(value, list):
                            value = [v for v in value if v not in [
                                "random", "none"]]
                            applied_values[key] = value

                        if isinstance(value, dict):
                            if "tags" in value:
                                applied_values[key] = value
                            else:
                                traverse(value)

                    case _:
                        applied_values[key] = selected

                        if (isinstance(value, dict) and "tags" in value):
                            if (isinstance(value["tags"], dict)):
                                applied_values[key] = value["tags"][selected]

        traverse(data)
        return applied_values

    def select_tags(self, rng, data):
        """
        Select tags randomly
        String: simply return the tags
        List/dict: choose tags randomly according to the parameters
        (e.g. probability, distribution, etc)
        """

        selected_tags = []
        match data:

            case str():
                selected_tags = data

            case list():
                selected_tags = rng.choice(data)

            case dict():
                tags = data.get("tags", [])
                prefix = data.get("prefix", "")
                suffix = data.get("suffix", "")
                p = data.get("probability", 1)
                d = data.get("distribution", np.ones(len(tags)))
                n = data.get("repeat", 1)

                # Probability
                if rng.random() > p:
                    return ""

                # Tag selection
                if isinstance(tags, str):
                    tags = [tags]

                if isinstance(tags, dict):
                    if tags.get("tags"):
                        tags = self.select_tags(rng, tags)
                    else:
                        subtags = []
                        for subtag in tags.values():
                            subtags.append(self.select_tags(rng, subtag))
                        tags = subtags

                # If n is a list, choose a
                # random number between the 2 first values
                if isinstance(n, list):
                    min_n = n[0]
                    max_n = min(n[1], len(data))
                    n = rng.integers(int(min_n), int(max_n))

                # Distribution
                d = np.resize(d, len(tags))
                d /= d.sum()
                d = d.tolist()

                selected_tags = rng.choice(
                    tags,
                    size=n,
                    p=d,
                    replace=False,
                )

                # Add prefix and suffix
                selected_tags = [
                    f"{prefix} {tag} {suffix}" for tag in selected_tags
                ]

                # Clean up
                selected_tags = self.stringify_tags(selected_tags)

        return selected_tags

    def build_inputs(self):
        """
        Build node's inputs according to the data
        """
        inputs = {"required": {}}

        def process_value(key, value):

            match value:

                # Handle strings
                case str():
                    inputs["required"][key] = ("STRING", {
                        "default": value,
                        "multiline": True
                    })

                # Handle list of strings
                case list() if all(isinstance(item, str) for item in value):
                    value.insert(0, "random")
                    value.append("none")
                    inputs["required"][key] = (value, {
                        "default": value[0] if value else ""
                    })

                # Handle dict recursively
                case dict():
                    if "hide" in value and value["hide"]:
                        return

                    if "tags" in value:
                        if isinstance(value["tags"], list):
                            process_value(key, value["tags"])
                        if isinstance(value["tags"], dict):
                            process_value(key, list(value["tags"].keys()))
                    else:
                        for child_key, child_value in dpath.search(
                                value, '*', yielded=True):
                            process_value(child_key, child_value)

        if not self.data.get("hide", False):
            for key, value in dpath.search(
                    self.data["tags"], '*', yielded=True):
                process_value(key, value)

        return inputs

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
    def stringify_tags(tags):
        """
        Return a string from a list of tags
        Remove extra commas and spaces
        """
        if isinstance(tags, np.ndarray):
            tags = tags.tolist()
        tags = ', '.join(map(str, tags))
        tags = ', '.join(filter(None, map(str.strip, tags.split(','))))
        return tags
