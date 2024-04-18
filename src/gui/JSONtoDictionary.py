# handleJSON.py
import json
from pathlib import Path


# opens a JSON file and returns the contents as a dictionary
def JSONtoDictionary(file_path):
    print(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            if file_path.suffix == ".json":
                return json.load(file)
            else:
                raise ValueError(
                    f"Invalid file format: {file_path}. Expected JSON file."
                )
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON from file: {file_path}. Error: {str(e)}")
