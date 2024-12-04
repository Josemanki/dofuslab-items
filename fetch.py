#!/usr/bin/env python3

from os import path, makedirs
import argparse
import json
import requests
import logging
import coloredlogs
import traceback

from constants import (
    DOFUSLAB_CATEGORIES,
    SETS_BASE_URL_D2,
    SETS_BASE_URL_D3,
    ITEMS_BASE_URL_D2,
    ITEMS_BASE_URL_D3,
    DOFUSLAB_GH_BASE_URL,
    BETA_SETS_BASE_URL_D2,
    BETA_ITEMS_BASE_URL_D2,
    BETA_SETS_BASE_URL_D3,
    BETA_ITEMS_BASE_URL_D3
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

coloredlogs.install(level="DEBUG", logger=logger, fmt="%(asctime)s %(levelname)s %(message)s")


# languages = ["en", "fr", "de", "es", "pt", "it"]
languages = ["en", "fr", "de", "es", "pt"]

# these will be changed in MAIN if we're using Dofus 3/Unity:
SETS_BASE_URL = SETS_BASE_URL_D2
ITEMS_BASE_URL = ITEMS_BASE_URL_D2

def get_set_files(beta: bool, unity: bool):
    for language in languages:
        if unity and beta:
            fetch_url = BETA_SETS_BASE_URL_D3
        elif unity:
            fetch_url = SETS_BASE_URL_D3
        elif beta:
            fetch_url = BETA_SETS_BASE_URL_D2
        else:
            fetch_url = SETS_BASE_URL_D2
        logger.info(f"Fetching set data for {language}")
        content = requests.get(fetch_url.format(language))
        parsed = content.json()

        dir_path = path.dirname(path.realpath(__file__))
        name = "{}_all.json".format(language)
        subfolder = "input/dofusdude/sets"
        complete_name = path.join(dir_path, subfolder, name)

        if not path.exists(path.join(dir_path, subfolder)):
            makedirs(path.join(dir_path, subfolder))

        with open(complete_name, "w", encoding="utf8") as file:
            json.dump(parsed, file, indent=4, ensure_ascii=False)


def get_item_files(beta: bool, unity: bool):
    for language in languages:
        if unity and beta:
            fetch_url = BETA_ITEMS_BASE_URL_D3
        elif unity:
            fetch_url = ITEMS_BASE_URL_D3
        elif beta:
            fetch_url = BETA_ITEMS_BASE_URL_D2
        else:
            fetch_url = ITEMS_BASE_URL_D2
        logger.info(f"Fetching item data for {language}")
        content = requests.get(fetch_url.format(language))
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
    parser.add_argument("-b", "--beta", action="store_true", help="Enables beta data fetch", default=False)
    parser.add_argument("-u", "--unity", action="store_true", help="Enables Dofus 3 endpoints", default=False)

    args = parser.parse_args()

    try:
        if args.datafile == "sets":
            logger.info("Fetching dodua set data...")
            get_set_files(beta=args.beta, unity=args.unity)
            logger.info("Fetched dodua set data.")
        elif args.datafile == "items":
            logger.info("Fetching dodua item data...")
            get_item_files(beta=args.beta, unity=args.unity)
            logger.info("Fetched dodua item data.")
        elif args.datafile == "dofuslab":
            logger.info("Fetching dofuslab data...")
            get_dofuslab_files()
            logger.info("Fetched dofuslab data.")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        traceback.print_exception(e)


if __name__ == "__main__":
    main()
