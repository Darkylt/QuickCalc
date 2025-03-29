import os
import sys

import yaml

# Determine base path (works for both script and executable)
if getattr(sys, "frozen", False):  # Running as a PyInstaller bundle
    BASE_PATH = sys._MEIPASS
else:  # Running as a normal Python script
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(BASE_PATH, "config.yml")

# Check if config.yml exists
if not os.path.exists(CONFIG_PATH):
    raise Exception(f"Configuration file not found: {CONFIG_PATH}")

try:
    with open(CONFIG_PATH, encoding="utf-8") as f:
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
