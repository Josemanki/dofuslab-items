#!/usr/bin/env python3

from os import path, makedirs
import json
import requests
from constants import (
    DOFUSLAB_CATEGORIES,
    SETS_BASE_URL,
    ITEMS_BASE_URL,
    DOFUSLAB_GH_BASE_URL,
)

languages = ["en", "fr", "de", "es", "pt", "it"]


def get_set_files():
    for language in languages:
        content = requests.get(SETS_BASE_URL.format(language))
        parsed = content.json()

        dir_path = path.dirname(path.realpath(__file__))
        name = "{}_all.json".format(language)
        subfolder = "input/dofusdude/sets"
        complete_name = path.join(dir_path, subfolder, name)

        if not path.exists(path.join(dir_path, subfolder)):
            makedirs(path.join(dir_path, subfolder))

        with open(complete_name, "w", encoding="utf8") as file:
            json.dump(parsed, file, indent=4, ensure_ascii=False)


def get_item_files():
    for language in languages:
        content = requests.get(ITEMS_BASE_URL.format(language))
        parsed = content.json()

        dir_path = path.dirname(path.realpath(__file__))
        name = "{}_all.json".format(language)
        subfolder = "input/dofusdude/equipment"
        complete_name = path.join(dir_path, subfolder, name)

        if not path.exists(path.join(dir_path, subfolder)):
            makedirs(path.join(dir_path, subfolder))

        with open(complete_name, "w", encoding="utf8") as file:
            json.dump(parsed, file, indent=4, ensure_ascii=False)


def get_dofuslab_files():
    for category in DOFUSLAB_CATEGORIES:
        content = requests.get(DOFUSLAB_GH_BASE_URL.format(category))
        parsed = content.json()

        dir_path = path.dirname(path.realpath(__file__))
        name = "{}.json".format(category)
        subfolder = "input/dofuslab"
        complete_name = path.join(dir_path, subfolder, name)

        if not path.exists(path.join(dir_path, subfolder)):
            makedirs(path.join(dir_path, subfolder))

        with open(complete_name, "w", encoding="utf8") as file:
            json.dump(parsed, file, indent=4, ensure_ascii=False)
