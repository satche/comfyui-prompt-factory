import numpy as np
import dpath
from .utils import load_nodes_config

RESERVED_KEYS = [
    "prefix",
    "suffix",
    "separator",
    "probability",
    "distribution",
    "number",
    "hide"
]


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

    def build_inputs(self):
        """
        Build node's inputs according to the data
        """
        inputs = {"required": {}}

        def process_value(key, value):

            match value:

                # Handle boolean
                case bool():
                    inputs["required"][key] = ("BOOLEAN", {
                        "default": value
                    })

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

                    if "tags" in value:

                        match value["tags"]:

                            # If tags is a list, just return it
                            # with all parameters from the dict
                            case list():
                                process_value(key, value["tags"])

                            # If tags has other sub-tags…
                            case dict():
                                display_group_labels = value.get(
                                    "group_labels", False)
                                if display_group_labels:
                                    # show the keys as input's label
                                    process_value(
                                        key, list(value["tags"].keys()))
                                else:
                                    # create a simple enable/disable checkbox
                                    process_value(key, True)

        if not self.data.get("hide", False):
            for key, value in dpath.search(
                    self.data["tags"], '*', yielded=True):
                process_value(key, value)

        return inputs

    def build_prompt(self, **args):
        """
        Build the prompt according to the node inputs
        Concatenate the tags and return the prompt
        """
        rng = np.random.default_rng(args["seed"])

        # Apply values from the node inputs
        input_values = self.apply_input_values(self.data["tags"], args)

        # Build tags randomly
        tags = {}
        for key, value in input_values.items():
            tags[key] = self.select_tags(rng, value)

        # Replace tags with corresponding variables
        variables = {}
        if "variables" in self.data:
            for key, value in self.data["variables"].items():
                variables[key] = self.select_tags(rng, value)
            tags = self.apply_variables(tags, variables)

        # Build and clean-up final prompt
        prompt = self.stringify_tags(tags.values(), ", ")
        return (prompt,)

    def apply_input_values(self, data, inputs):
        """
        Apply what has been selected in the node inputs
        Can be "random", "none", or a selected value
        """
        applied_values = {}

        def traverse(data):

            for key, value in data.items():

                selected = inputs.get(key, "random")

                match selected:

                    # If "none" or false, just ignore the tag
                    case "none" | False:
                        continue

                    # If "random", return the string, list or dict
                    # according to the JSON config file
                    case "random":
                        applied_values[key] = value

                        if isinstance(value, dict) and not value.get("tags"):
                            traverse(value)

                    # If a value is selected, just return it
                    case _:
                        applied_values[key] = selected

                        if selected is True:
                            applied_values[key] = value
                            continue

                        if isinstance(value, dict):
                            prefix = value.get("prefix", "")
                            suffix = value.get("suffix", "")
                            applied_values[key] = f"{prefix}{selected}{suffix}"

                            if isinstance(value.get("tags"), dict):
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

        if isinstance(data, (str, list)):
            data = {"tags": data}

        # Probability
        p = data.get("probability", 1)
        if rng.random() > p:
            return ""

        # Tag selection
        tags = data.get("tags", [])
        prefix = data.get("prefix", "")
        suffix = data.get("suffix", "")

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

        # Number of tags to select
        n = data.get("number", 1)
        if isinstance(n, int) and n > len(tags):
            n = len(tags)

        # If n is a list, choose a
        # random number between the 2 first values
        if isinstance(n, list):
            min_n = n[0]
            max_n = min(n[1], len(tags))
            n = rng.integers(int(min_n), int(max_n))

        # Distribution: how likely each tag is to be selected
        # Normalize the distribution so the sum = 1
        # Add missing values if necessary
        d = data.get("distribution", np.ones(len(tags)))
        if np.sum(d) > 1:
            d = d / np.sum(d)
            d = np.append(d, np.zeros(len(tags) - len(d)))
        elif len(d) < len(tags):
            n_remaining_tags = len(tags) - len(d)
            remaining_d = 1 - np.sum(d)
            d = np.append(
                d, np.full(
                    n_remaining_tags,
                    remaining_d / n_remaining_tags
                )
            )

        # Chose between the tags
        if tags:
            selected_tags = rng.choice(
                tags,
                size=n,
                p=d,
                replace=False,
            )
            selected_tags = sorted(
                selected_tags, key=lambda x: tags.index(x))

        # Recursive choice (grouped tag)
        else:
            for key, value in data.items():
                if key not in RESERVED_KEYS:
                    selected_tags.append(self.select_tags(rng, value))

        # Add prefix and suffix
        selected_tags = [
            f"{prefix}{tag}{suffix}" for tag in selected_tags
        ]

        # Clean up
        separator = data.get("separator", ",")
        selected_tags = self.stringify_tags(selected_tags, separator)

        return selected_tags

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
        for key, value in tags.items():
            for var_key, var_value in variables.items():
                value = value.replace("{"+var_key+"}", f"{var_value}")
            tags[key] = value
        return tags

    @staticmethod
    def stringify_tags(tags, separator=""):
        """
        Return a string from a list of tags
        Remove extra commas and spaces
        """
        if isinstance(tags, np.ndarray):
            tags = tags.tolist()
        tags = separator.join(map(str, tags))

        # Remove extra comma and spaces
        tags = tags.replace(", ", ",").replace(
            ",,", ",").replace(",", ", ").strip(", ")

        return tags
