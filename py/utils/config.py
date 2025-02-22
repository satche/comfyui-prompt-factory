import os
import json
from glob import glob

ROOT_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'))

DEFAULT_PATH = "config.default/nodes"
CUSTOM_PATH = "config/nodes"

RESERVED_KEYS = [
    "prefix",
    "suffix",
    "separator",
    "probability",
    "distribution",
    "number",
    "hide",
    "group_labels"
]


def load_nodes_config():
    "Load and merge all node's config files"
    config_path = chose_config()
    config_files = glob(os.path.join(
        config_path, "**", "*.json"), recursive=True)

    config = {}
    for path in config_files:
        with open(path, 'r') as config_file:
            config_data = json.load(config_file)
            node_id = os.path.splitext(os.path.basename(path))[0]
            config[node_id] = config_data

    return config


def chose_config():
    "Chose between default and custom config"
    custom_config_path = os.path.join(ROOT_PATH, CUSTOM_PATH)

    if os.path.exists(custom_config_path):
        config_path = CUSTOM_PATH
    else:
        config_path = DEFAULT_PATH

    absolute_config_path = os.path.join(ROOT_PATH, config_path)

    return absolute_config_path
