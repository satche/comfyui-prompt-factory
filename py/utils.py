import os
import json


def load_config():
    config_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "../config/config.json")
    with open(config_path, 'r') as config_file:
        return json.load(config_file)
