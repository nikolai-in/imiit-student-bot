"""Reads data for student bot."""
import json
import os
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup


script_dir = os.path.dirname(__file__)


def load_responses() -> dict:
    """Reads data from response.json in package."""
    with open(os.path.join(script_dir, "response.json")) as json_file:
        return json.load(json_file)


def get_groups() -> dict:
    group_list = requests.get("https://miit.ru/timetable/", allow_redirects=True).text
    soup = BeautifulSoup(group_list, "html.parser")
    return {
        group.string.strip().lower(): group["href"].strip("/timetable/")
        for group in soup.find_all("a", href=re.compile(r"\/timetable\/\d*"))
    }


def get_timetable(group_id):
    timetables_df = pd.read_html(f"https://miit.ru/timetable/{group_id}", index_col=0)
    timetables = []
    for timetable in timetables_df:
        timetable.dropna(axis=1, how="all", inplace=True)
        timetables.append(timetable.to_dict(orient="dict"))
    return timetables
