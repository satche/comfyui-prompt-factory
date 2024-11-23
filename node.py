import numpy as np
import dpath
from .utils import load_config


class Node:

    def __init__(self):
        config = load_config()
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
    CATEGORY = "⚙️ Prompt Factory"

    def build_prompt(self, **args):
        """
        Build the prompt according to tags and return it
        """
        input_values = self.apply_input_values(self.data["tags"], args)

        tags = {}
        for key, value in input_values.items():
            tags[key] = self.select_tags(value, args["seed"])

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

                if "tags" in value:
                    value = value["tags"]

                match selected:
                    case "none":
                        continue

                    case "random":

                        if isinstance(value, list):
                            value = [v for v in value if v not in [
                                "random", "none"]]
                            applied_values[key] = value

                        if isinstance(value, dict) and "tags" not in value:
                            traverse(value)

                    case _:
                        applied_values[key] = selected

        traverse(data)
        return applied_values

    def select_tags(self, tags, seed=0):
        """
        Select the given tags
        Fallback to chose a random tag according to RNG
        """

        selected_tags = []
        rng = np.random.default_rng(seed)

        match tags:

            case str():
                selected_tags = tags

            case list():
                selected_tags = rng.choice(tags)

            case dict():
                p = tags.get("probability", 1)
                n = tags.get("number", 1)
                d = tags.get("distribution", np.ones(len(tags)))

                # Probability
                if rng.random() > p:
                    return ""

                # If n is a list, choose a
                # random number between the 2 first values
                if isinstance(n, list):
                    min_n = n[0]
                    max_n = min(n[1], len(tags))
                    n = rng.integers(int(min_n), int(max_n))

                # Distribution
                d = np.resize(d, len(tags))
                d /= d.sum()
                d = d.tolist()

                # Tag selection
                selected_tags = rng.choice(
                    tags,
                    size=n,
                    p=d,
                    replace=False,
                )

        return selected_tags

    def build_inputs(self):
        """Build node's inputs according to the data"""
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

                # Handle dict
                case dict():
                    if "hide" in value and value["hide"]:
                        return
                    if "tags" in value and isinstance(value["tags"], list):
                        process_value(key, value["tags"])
                    else:
                        for path, value in dpath.search(
                                value, '*', yielded=True):
                            process_value(path, value)

        for key, value in dpath.search(self.data["tags"], '*', yielded=True):
            process_value(key, value)

        return inputs

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
