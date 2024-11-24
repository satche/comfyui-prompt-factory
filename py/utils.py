import os
import json


def load_config():
    """
    Load json file from the config.default folder
    """
    user_folder_name = "config"
    default_folder_name = "config.default"
    root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    # User default config as fallback
    config_folder_name = user_folder_name

    if not os.path.exists(os.path.join(root_path, config_folder_name)):
        config_folder_name = default_folder_name

    # Load config
    config_file_path = os.path.join(
        root_path, config_folder_name, "config.json")

    with open(config_file_path, 'r') as config_file:
        return json.load(config_file)
