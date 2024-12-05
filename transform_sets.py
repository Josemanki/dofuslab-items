#!/usr/bin/env python3

from os import path, makedirs
import json
import argparse
import logging
import coloredlogs
from constants import NORMAL_STAT_MAP


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

coloredlogs.install(level="INFO", logger=logger, fmt="%(asctime)s %(levelname)s %(message)s")

# from fetch import get_set_files, get_dofuslab_files
# try:
#     get_set_files()
#     # get_dofuslab_files()
# except Exception as e:
#     logger.error(f"An error occurred: {str(e)}")


def item_exists(name, dofuslab_sets_json):
    for i in dofuslab_sets_json:
        if i["name"]["en"] == name:
            return True


def remove_item(name, dofuslab_sets_json):
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
    dofuslab_bonuses = {}

    logger.debug(f"Number of bonuses: {len(bonuses)}")

    for bonus_key, bonus_values in bonuses.items():
        if not bonus_values:
            continue

        set_bonus = []
        for bonus_value in bonus_values:
            if bonus_value["type"]["name"] in NORMAL_STAT_MAP:
                set_bonus.append(
                    {"stat": NORMAL_STAT_MAP[bonus_value["type"]["name"]], "value": bonus_value["int_minimum"], "altStat": None}
                )
        dofuslab_bonuses[bonus_key] = set_bonus

    return dofuslab_bonuses


def transform_sets(dofusdude_data, dofuslab_sets_json, skip: bool = True, replace: bool = False):
    # List of sets
    final_sets = []

    if not path.exists("output"):
        makedirs("output")

    for dset in dofusdude_data["en"]["sets"]:
        # skip set if the name contains " Ceremonial Set" - the leading space is important
        if " Ceremonial Set" in dset["name"]:
            logger.info(f"Skipping ceremonial set: {dset["name"]}")
            continue

        logger.debug(f"Transforming: {dset['name']}")
        logger.debug(f"Set data: {dset}")

        if replace and item_exists(dset["name"], dofuslab_sets_json):
            # replace set if it already exists
            logger.debug(f"Set {dset['name']} already exists, removing from array to replace with doduda...")
            remove_item(dset["name"], dofuslab_sets_json)

        if skip and item_exists(dset["name"], dofuslab_sets_json):
            # skip set if it already exists
            continue

        if "effects" in dset:
            logger.debug(f"Adding {dset['name']}...")

            # Locales
            en_set = find_localized_item(dset["ankama_id"], dofusdude_data["en"]["sets"])
            fr_set = find_localized_item(dset["ankama_id"], dofusdude_data["fr"]["sets"])
            es_set = find_localized_item(dset["ankama_id"], dofusdude_data["es"]["sets"])
            de_set = find_localized_item(dset["ankama_id"], dofusdude_data["de"]["sets"])
            pt_set = find_localized_item(dset["ankama_id"], dofusdude_data["pt"]["sets"])
            it_set = find_localized_item(dset["ankama_id"], dofusdude_data["en"]["sets"])

            rebuilt_set = {
                "id": str(dset["ankama_id"]),
                "name": {
                    "en": en_set["name"],
                    "fr": fr_set["name"],
                    "de": de_set["name"],
                    "es": es_set["name"],
                    "pt": pt_set["name"],
                    "it": it_set["name"],
                },
                "bonuses": generate_set_bonuses(en_set["effects"]),
            }
            final_sets.append(rebuilt_set)
            logger.info(f"Transformed:  {dset['name']}.")

    with open("output/sets.json", "w+", encoding="utf8", newline="\r\n") as outfile:
        outfile.write(json.dumps(final_sets, ensure_ascii=False, indent=4))
        outfile.close()


def main():
    parser = argparse.ArgumentParser(
        description="Transforms sets json data from doduda into dofuslab format",
    )
    parser.add_argument(
        "-s",
        "--skip",
        action="store_true",
        help="Skips elements that already exist in the dofuslab data",
        default=False,
    )
    parser.add_argument(
        "-r",
        "--replace",
        action="store_true",
        help="Replaces elements if they already exist in the dofuslab data",
        default=False,
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enables verbose debug output", default=False
    )
    parser.add_argument(
        "-i",
        "--ignore_dofuslab",
        action="store_true",
        help="Ignores dofuslab data and regenerates entirely from doduda",
        default=False
    )

    args = parser.parse_args()

    logger.info("Note: this assumes set data has been downloaded via fetch.py")

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        coloredlogs.install(level="DEBUG", logger=logger, fmt="%(asctime)s %(levelname)s %(message)s")

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
    dofuslab_sets_json = []
    if not args.ignore_dofuslab:
        dofuslab_json = open("input/dofuslab/sets.json")
        dofuslab_sets_json = json.load(dofuslab_json)
        dofuslab_json.close()

    # sort sets for convenience and consistency of output:
    en_dofusdude_data["sets"] = sorted(en_dofusdude_data["sets"], key=lambda k: k["ankama_id"])
    dofuslab_sets_json = sorted(dofuslab_sets_json, key=lambda d: d["id"])

    dofusdude_data = {}
    dofusdude_data["en"] = en_dofusdude_data
    dofusdude_data["fr"] = fr_dofusdude_data
    dofusdude_data["es"] = es_dofusdude_data
    dofusdude_data["de"] = de_dofusdude_data
    dofusdude_data["it"] = en_dofusdude_data
    dofusdude_data["pt"] = pt_dofusdude_data

    transform_sets(dofusdude_data, dofuslab_sets_json, skip=args.skip, replace=args.replace)


if __name__ == "__main__":
    main()
