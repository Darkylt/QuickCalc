import os

import PyInstaller.__main__

icon_path = "assets/icon.ico"
config_path = "config.yml"
separator = ";" if os.name == "nt" else ":"

PyInstaller.__main__.run(
    [
        "src/run.py",
        "--onefile",
        "--noconsole",
        "--icon=assets/icon.ico",
        "--name=QuickCalc",
        f"--add-data={config_path}{separator}.",
        f"--add-data={icon_path}{separator}.",
    ]
)

print("Build complete! Check the 'dist' folder for the executable.")
