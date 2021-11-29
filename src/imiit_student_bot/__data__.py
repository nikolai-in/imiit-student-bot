"""Reads data for student bot."""
import json
import os

script_dir = os.path.dirname(__file__)


def load_responses() -> dict:
    """Reads data from response.json in package."""
    with open(os.path.join(script_dir, "response.json")) as json_file:
        return json.load(json_file)
