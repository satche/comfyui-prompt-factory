import os
import json
from glob import glob

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DEFAULT_PATH = "config.default/nodes"
CUSTOM_PATH = "config/nodes"


def load_nodes_config():
    """
    Load and merge all node's config files
    """
    config_path = get_config_path()
    config_files = glob(os.path.join(
        config_path, "**", "*.json"), recursive=True)

    config = {}
    for path in config_files:
        with open(path, 'r') as config_file:
            config_data = json.load(config_file)
            node_id = os.path.splitext(os.path.basename(path))[0]
            config[node_id] = config_data

    return config


def get_config_path():
    config_path = CUSTOM_PATH if os.path.exists(
        os.path.join(ROOT_PATH, CUSTOM_PATH)) else DEFAULT_PATH

    return os.path.join(ROOT_PATH, config_path)
