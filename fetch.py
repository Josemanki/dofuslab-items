#!/usr/bin/env python3

from os import path, makedirs
import argparse
import json
import requests
import logging
import coloredlogs

from constants import (
    DOFUSLAB_CATEGORIES,
    SETS_BASE_URL,
    ITEMS_BASE_URL,
    DOFUSLAB_GH_BASE_URL,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

coloredlogs.install(level="DEBUG", logger=logger, fmt="%(asctime)s %(levelname)s %(message)s")


languages = ["en", "fr", "de", "es", "pt", "it"]


def get_set_files():
    for language in languages:
        logger.info(f"Fetching set data for {language}")
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
        logger.info(f"Fetching item data for {language}")
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
        logger.info(f"Fetching dofuslab data for {category}")
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetches data from dodua to populate json data for dofuslab",
    )
    parser.add_argument("datafile", type=str, help="the data to fetch")

    args = parser.parse_args()

    try:
        if args.datafile == "sets":
            logger.info("Fetching dodua set data...")
            get_set_files()
            logger.info("Fetched dodua set data.")
        elif args.datafile == "items":
            logger.info("Fetching dodua item data...")
            get_item_files()
            logger.info("Fetched dodua item data.")
        elif args.datafile == "dofuslab":
            logger.info("Fetching dofuslab data...")
            get_dofuslab_files()
            logger.info("Fetched dofuslab data.")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
