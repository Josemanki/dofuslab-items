#!/usr/bin/env python3

import json
import logging
import coloredlogs
from constants import NORMAL_STAT_MAP

from fetch import get_set_files, get_dofuslab_files

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

coloredlogs.install(level="DEBUG", logger=logger, fmt="%(asctime)s %(levelname)s %(message)s")

# try:
#     get_set_files()
#     # get_dofuslab_files()
# except Exception as e:
#     logger.error(f"An error occurred: {str(e)}")

# Opening all languages in order to populate localized names
# This will be a list of requests in the future, not so many files being opened
dofusdude_json_en = open("input/dofusdude/sets/en_all.json")
en_dofusdude_data = json.load(dofusdude_json_en)
dofusdude_json_en.close()

dofusdude_json_fr = open("input/dofusdude/sets/fr_all.json")
fr_dofusdude_data = json.load(dofusdude_json_fr)
dofusdude_json_fr.close()

dofusdude_json_es = open("input/dofusdude/sets/es_all.json")
es_dofusdude_data = json.load(dofusdude_json_es)
dofusdude_json_es.close()

dofusdude_json_pt = open("input/dofusdude/sets/pt_all.json")
pt_dofusdude_data = json.load(dofusdude_json_pt)
dofusdude_json_pt.close()

dofusdude_json_de = open("input/dofusdude/sets/de_all.json")
de_dofusdude_data = json.load(dofusdude_json_de)
dofusdude_json_de.close()

dofusdude_json_it = open("input/dofusdude/sets/it_all.json")
it_dofusdude_data = json.load(dofusdude_json_it)
dofusdude_json_it.close()

# Dofuslab sets
dofuslab_json = open("input/dofuslab/sets.json")
dofuslab_sets_json = json.load(dofuslab_json)
dofuslab_json.close()

# List of sets
final_sets = []

# sort sets for convenience and consistency of output:
en_dofusdude_data["sets"] = sorted(en_dofusdude_data["sets"], key=lambda k: k["ankama_id"])
dofuslab_sets_json = sorted(dofuslab_sets_json, key=lambda d: d["id"])


def item_exists(name):
    for i in dofuslab_sets_json:
        if i["name"]["en"] == name:
            return True


def remove_item(name):
    for i in dofuslab_sets_json:
        if i["name"]["en"] == name:
            dofuslab_sets_json.remove(i)
            break


def find_localized_set(set_id, language_data):
    try:
        found = next(set for set in language_data if set["ankama_id"] == set_id)
        return found
    except StopIteration:
        logger.error(f"Localized set not found for ID {set_id}!")


def find_localized_item(item_id, language_data):
    try:
        found = next(item for item in language_data if item["ankama_id"] == item_id)
        return found
    except StopIteration:
        logger.error(f"Localized item not found for ID {item_id}!")


def generate_set_bonuses(bonuses):
    # Bonuses is a 2D array from Dofusdude, that needs to be transformed to an object, with number keys and arrays as values
    transformed = {}

    logger.debug(f"Number of bonuses: {len(bonuses)}")

    for i in range(1, len(bonuses) + 1):
        transformed[i + 1] = []

        for bonus in bonuses[i - 1]:
            if bonus["type"]["name"] in NORMAL_STAT_MAP:
                transformed[i + 1].append(
                    {"stat": NORMAL_STAT_MAP[bonus["type"]["name"]], "value": bonus["int_minimum"], "altStat": None}
                )
    return transformed


def transform_sets(skip: bool = True, replace: bool = False):
    for set in en_dofusdude_data["sets"]:
        logger.info(f"Transforming {set["name"]}...")
        logger.debug(f"Set: {set}")

        # skip set if the name contains " Ceremonial Set"
        if " Ceremonial Set" in set["name"]:
            logger.info(f"Skipping set {set["name"]}")
            continue

        if replace and item_exists(set["name"]):
            # replace set if it already exists
            logger.debug(f"Set {set["name"]} already exists, removing from array to replace with doduda...")
            remove_item(set["name"])

        if skip and item_exists(set["name"]):
            # skip set if it already exists
            continue

        if "effects" in set:
            logger.info("Adding {} to items...".format(set["name"]))

            # Locales
            en_set = find_localized_item(set["ankama_id"], en_dofusdude_data["sets"])
            fr_set = find_localized_item(set["ankama_id"], fr_dofusdude_data["sets"])
            es_set = find_localized_item(set["ankama_id"], es_dofusdude_data["sets"])
            de_set = find_localized_item(set["ankama_id"], de_dofusdude_data["sets"])
            it_set = find_localized_item(set["ankama_id"], it_dofusdude_data["sets"])
            pt_set = find_localized_item(set["ankama_id"], pt_dofusdude_data["sets"])

            rebuilt_set = {
                "id": str(set["ankama_id"]),
                "name": {
                    "en": en_set["name"],
                    "fr": fr_set["name"],
                    "de": de_set["name"],
                    "it": it_set["name"],
                    "es": es_set["name"],
                    "pt": pt_set["name"],
                },
                "bonuses": generate_set_bonuses(en_set["effects"]),
            }
            final_sets.append(rebuilt_set)
            logger.info("Added {} to items".format(set["name"]))

        with open("output/sets.json", "w+", encoding="utf8") as outfile:
            outfile.write(json.dumps(dofuslab_sets_json + final_sets, ensure_ascii=False, indent=4))
            outfile.close()


__main__ = transform_sets(skip=False, replace=True)
