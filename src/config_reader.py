import os

import yaml

CONFIG_FILENAME = "config.yml"

config_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), CONFIG_FILENAME
)

try:
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    raise Exception(
        "Configuration file not found. Please make sure the config.yml file is in the Main Folder."
    )
except yaml.YAMLError:
    raise Exception(
        "Error parsing the configuration file. Invalid YAML format. Please make sure the config.yml is formatted correctly."
    )


class App:
    hotkey = config["Key"]
