#!/usr/bin/env python3

from os import path, makedirs
import json
import argparse
import logging
import coloredlogs
import requests
from constants import (
    CUSTOM_STAT_MAP,
    NORMAL_STAT_MAP,
    PET_ITEM_TYPES,
    WEAPON_TYPES,
    WEAPON_STAT_MAP,
    IGNORED_CATEGORIES,
    IGNORED_ITEM_TYPES,
    IGNORED_ITEM_IDS,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

coloredlogs.install(level="INFO", logger=logger, fmt="%(asctime)s %(levelname)s %(message)s")

# from fetch import get_item_files
# try:
#     get_item_files()
# except Exception as e:
#     print(f"An error occurred: {str(e)}")


def item_exists(name, dofuslab_data):
    # item_types = {"items", "mounts", "pets", "rhineetles", "weapons"}
    for item_type in dofuslab_data:
        for i in dofuslab_data[item_type]:
            if i["name"]["en"] == name:
                return True


def remove_item(name, dofuslab_data):
    for item_type in dofuslab_data:
        for i in dofuslab_data[item_type]:
            if i["name"]["en"] == name:
                dofuslab_data[item_type].remove(i)
                break


def categorize_item(item, data):
    """
    Adds the item to the appropriate list in data
    """
    if item["itemType"] in PET_ITEM_TYPES:
        data["pets"].append(item)
        logger.info(f"Added:  {item["name"]["en"]} to pets")

    elif item["itemType"] in WEAPON_TYPES:
        data["weapons"].append(item)
        logger.info(f"Added:  {item["name"]["en"]} to weapons")

    elif item["itemType"] == "Mount" and item["name"]["en"].contains("Rhineetle"):
        data["rhineetles"].append(item)
        logger.info(f"Added:  {item["name"]["en"]} to rhineetles")

    elif item["itemType"] == "Mount":
        data["mounts"].append(item)
        logger.info(f"Added:  {item["name"]["en"]} to mounts")

    else:
        # itemType can be "Cloak", etc
        data["items"].append(item)
        logger.info(f"Added:  {item["name"]["en"]} to items")


def format_image(image_urls):
    # return image_urls["sd"].split("item/")[1]
    return "item/" + image_urls["icon"].split("item/")[1]


def format_image_and_download(image_urls):
    dir_path = path.dirname(path.realpath(__file__))
    img_id = image_urls["sd"].split("item/")[1]
    subfolder = "output/images"
    complete_name = path.join(dir_path, subfolder, img_id)
    img_data = requests.get(image_urls["icon"]).content

    if not path.exists(path.join(dir_path, subfolder)):
        makedirs(path.join(dir_path, subfolder))

    with open(complete_name, "wb") as handler:
        handler.write(img_data)
    return img_id


def transform_conditions(conditions):
    retConditions = {"conditions": {}}
    condition_list = {"and": []}
    for condition in conditions:
        condition_list["and"].append(
            {
                "stat": condition["element"]["name"].upper().replace(" ", "_"),
                "operator": condition["operator"],
                "value": condition["int_value"],
            }
        )
    retConditions["conditions"] = condition_list
    retConditions["customConditions"] = {}
    return retConditions


def transform_stats(stats):
    normal_stats = []
    weapon_stats = []
    custom_stats = {"en": [], "fr": [], "de": [], "es": [], "it": [], "pt": []}

    for stat in stats:
        if stat["type"]["name"] in NORMAL_STAT_MAP:
            normal_stats.append(
                {
                    "stat": NORMAL_STAT_MAP[stat["type"]["name"]],
                    "minStat": stat["int_minimum"] if stat["int_maximum"] != 0 else None,
                    "maxStat": stat["int_maximum"] if stat["int_maximum"] != 0 else stat["int_minimum"],
                }
            )
        elif stat["type"]["name"] in WEAPON_STAT_MAP:
            weapon_stats.append(
                {
                    "stat": WEAPON_STAT_MAP[stat["type"]["name"]],
                    "minStat": stat["int_minimum"] if stat["int_maximum"] != 0 else None,
                    "maxStat": stat["int_maximum"] if stat["int_maximum"] != 0 else stat["int_minimum"],
                }
            )
        elif stat["type"]["name"] in CUSTOM_STAT_MAP:
            custom_stats["en"].append(stat["formatted"])
            custom_stats["fr"].append(stat["type"]["id"])
            custom_stats["de"].append(stat["type"]["id"])
            custom_stats["es"].append(stat["type"]["id"])
            custom_stats["it"].append(stat["type"]["id"])
            custom_stats["pt"].append(stat["type"]["id"])

    return {
        "stats": normal_stats,
        "weaponStats": weapon_stats,
        "customStats": custom_stats if len(custom_stats["en"]) > 0 else {},
    }


def find_localized_item(item_id, language_data):
    try:
        found = next(item for item in language_data if item["ankama_id"] == item_id)
        return found
    except StopIteration:
        logger.warning(f"Localization not found for id {item_id}")


def localize_custom_stats_from_id(stat_ids, item_stats):
    custom_stats = []

    for stat_id in stat_ids:
        found = next(item for item in item_stats if item["type"]["id"] == stat_id)
        custom_stats.append(found["formatted"])

    return custom_stats


def transform_items(dofusdude_data, dofuslab_data, skip=True, replace=False, download_imgs=False):
    # dictionary of lists of items
    final_data = {}
    for item_type in {"items", "mounts", "pets", "rhineetles", "weapons"}:
        final_data[item_type] = []

    if not path.exists("output"):
        makedirs("output")

    for item in dofusdude_data["en"]["items"]:
        if skip and item_exists(item["name"], dofuslab_data):
            logger.info(f"Skipping: {item["name"]}")
            continue
        elif replace and item_exists(item["name"], dofuslab_data):
            remove_item(item["name"], dofuslab_data)
        elif item["type"]["name"] in IGNORED_ITEM_TYPES:
            logger.info(f"Skipping: {item["name"]}")
            continue
        elif item["ankama_id"] in IGNORED_ITEM_IDS:
            logger.info(f"Skipping: {item["name"]}")
            continue
        elif item["is_weapon"]:
            # WEAPON TRANSFORMATION
            if "effects" in item and item["type"]["name"] not in IGNORED_CATEGORIES:
                logger.debug(f"Adding: {item["name"]}")
                item_effects = transform_stats(item["effects"])
                custom_stats = {}

                # Locales
                en_item = find_localized_item(item["ankama_id"], dofusdude_data["en"]["items"])
                fr_item = find_localized_item(item["ankama_id"], dofusdude_data["fr"]["items"])
                es_item = find_localized_item(item["ankama_id"], dofusdude_data["es"]["items"])
                de_item = find_localized_item(item["ankama_id"], dofusdude_data["de"]["items"])
                it_item = find_localized_item(item["ankama_id"], dofusdude_data["it"]["items"])
                pt_item = find_localized_item(item["ankama_id"], dofusdude_data["pt"]["items"])

                if "en" in item_effects["customStats"]:
                    custom_stats = {
                        "en": item_effects["customStats"]["en"],
                        "fr": localize_custom_stats_from_id(item_effects["customStats"]["fr"], fr_item["effects"]),
                        "de": localize_custom_stats_from_id(item_effects["customStats"]["de"], de_item["effects"]),
                        "it": localize_custom_stats_from_id(item_effects["customStats"]["it"], it_item["effects"]),
                        "es": localize_custom_stats_from_id(item_effects["customStats"]["es"], es_item["effects"]),
                        "pt": localize_custom_stats_from_id(item_effects["customStats"]["pt"], pt_item["effects"]),
                    }

                rebuilt_item = {
                    # this needs to be a str, but for the purposes of sorting, we'll make it an int
                    # and convert it to a str later.
                    # "dofusID": str(item["ankama_id"]),
                    "dofusID": item["ankama_id"],
                    "name": {
                        "en": en_item["name"],
                        "fr": fr_item["name"],
                        "de": de_item["name"],
                        "it": it_item["name"],
                        "es": es_item["name"],
                        "pt": pt_item["name"],
                    },
                    "itemType": item["type"]["name"],
                    "setID": str(item["parent_set"]["id"]) if "parent_set" in item else None,
                    "level": item["level"],
                    "stats": item_effects["stats"],
                    "weaponStats": {
                        "apCost": item["ap_cost"],
                        "usesPerTurn": item["max_cast_per_turn"],
                        "minRange": item["range"]["min"] if item["range"]["min"] != item["range"]["max"] else None,
                        "maxRange": item["range"]["max"],
                        "baseCritChance": item["critical_hit_probability"],
                        "critBonusDamage": item["critical_hit_bonus"],
                        "weapon_effects": item_effects["weaponStats"],
                    },
                    "customStats": custom_stats,
                    "conditions": transform_conditions(item["conditions"])
                    if "conditions" in item
                    else {"conditions": {}, "customConditions": {}},
                    "imageUrl": format_image(item["image_urls"]),
                }
                categorize_item(rebuilt_item, final_data)
                if download_imgs:
                    format_image_and_download(item["image_urls"])
        else:
            # ITEM TRANSFORMATION
            if "effects" in item and item["type"]["name"] not in IGNORED_CATEGORIES:
                logger.debug(f"Adding: {item["name"]}")
                item_effects = transform_stats(item["effects"])
                custom_stats = {}

                # Locales
                en_item = find_localized_item(item["ankama_id"], dofusdude_data["en"]["items"])
                fr_item = find_localized_item(item["ankama_id"], dofusdude_data["fr"]["items"])
                es_item = find_localized_item(item["ankama_id"], dofusdude_data["es"]["items"])
                de_item = find_localized_item(item["ankama_id"], dofusdude_data["de"]["items"])
                it_item = find_localized_item(item["ankama_id"], dofusdude_data["it"]["items"])
                pt_item = find_localized_item(item["ankama_id"], dofusdude_data["pt"]["items"])

                if "en" in item_effects["customStats"]:
                    custom_stats = {
                        "en": item_effects["customStats"]["en"],
                        "fr": localize_custom_stats_from_id(item_effects["customStats"]["fr"], fr_item["effects"]),
                        "de": localize_custom_stats_from_id(item_effects["customStats"]["de"], de_item["effects"]),
                        "it": localize_custom_stats_from_id(item_effects["customStats"]["it"], it_item["effects"]),
                        "es": localize_custom_stats_from_id(item_effects["customStats"]["es"], es_item["effects"]),
                        "pt": localize_custom_stats_from_id(item_effects["customStats"]["pt"], pt_item["effects"]),
                    }

                rebuilt_item = {
                    # this needs to be a str, but for the purposes of sorting, we'll make it an int
                    # and convert it to a str later.
                    # "dofusID": str(item["ankama_id"]),
                    "dofusID": item["ankama_id"],
                    "name": {
                        "en": en_item["name"],
                        "fr": fr_item["name"],
                        "de": de_item["name"],
                        "it": it_item["name"],
                        "es": es_item["name"],
                        "pt": pt_item["name"],
                    },
                    "itemType": item["type"]["name"],
                    "setID": str(item["parent_set"]["id"]) if "parent_set" in item else None,
                    "level": item["level"],
                    "stats": item_effects["stats"],
                    "customStats": custom_stats,
                    "conditions": transform_conditions(item["conditions"])
                    if "conditions" in item
                    else {"conditions": {}, "customConditions": {}},
                    "imageUrl": format_image(item["image_urls"]),
                }
                categorize_item(rebuilt_item, final_data)
                if download_imgs:
                    format_image_and_download(item["image_urls"])

    # more processing to remove extra conditions on items:
    for item in final_data["pets"]:
        # for some reason, we have a "= 0" condition on our petsmounts
        conds_to_remove = {"conditions": {"and": [{"stat": "", "operator": "=", "value": 1}]}, "customConditions": {}}
        # remove it:
        if item["conditions"] == conds_to_remove:
            logger.info(f"Removing extraneous conditions on {item["name"]["en"]}")
            item["conditions"] = {"conditions": {}, "customConditions": {}}

    # todo: fix the "or" conditions from doduda, which are currently unsupported

    for data_block in final_data:
        data_block = sorted(data_block, key=lambda d: d["dofusID"])

        for item in data_block:
            item["dofusID"] = str(item["dofusID"])


    with open("output/items.json", "w+", encoding="utf8") as outfile:
        outfile.write(json.dumps(dofuslab_data["items"] + final_data["items"], indent=4, ensure_ascii=False))
        outfile.close()

    # this doesn't currently populate
    # with open("output/mounts.json", "w+", encoding="utf8") as outfile:
    #     outfile.write(json.dumps(dofuslab_data["mounts"] + final_data["mounts"], indent=4, ensure_ascii=False))
    #     outfile.close()

    with open("output/pets.json", "w+", encoding="utf8") as outfile:
        outfile.write(json.dumps(dofuslab_data["pets"] + final_data["pets"], indent=4, ensure_ascii=False))
        outfile.close()

    # this doesn't currently populate, so skip writing it
    # with open("output/rhineetles.json", "w+", encoding="utf8") as outfile:
    #     outfile.write(json.dumps(dofuslab_data["rhineetles"] + final_data["rhineetles"], indent=4, ensure_ascii=False))
    #     outfile.close()

    with open("output/weapons.json", "w+", encoding="utf8") as outfile:
        outfile.write(json.dumps(dofuslab_data["weapons"] + final_data["weapons"], indent=4, ensure_ascii=False))
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
    parser.add_argument("-v", "--verbose", action="store_true", help="Enables verbose debug output", default=False)
    parser.add_argument(
        "-i",
        "--ignore_dofuslab",
        action="store_true",
        help="Ignores dofuslab data and regenerates entirely from doduda",
        default=False,
    )
    parser.add_argument(
        "-d",
        "--download_imgs",
        action="store_true",
        help="Downloads images from doduda for items",
        default=False,
    )

    args = parser.parse_args()

    logger.info("Note: this assumes set data has been downloaded via fetch.py")

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        coloredlogs.install(level="DEBUG", logger=logger, fmt="%(asctime)s %(levelname)s %(message)s")

    # Opening all languages in order to populate localized names
    # This will be a list of requests in the future, not so many files being opened

    dofusdude_json_en = open("input/dofusdude/equipment/en_all.json")
    en_dofusdude_data = json.load(dofusdude_json_en)
    dofusdude_json_en.close()

    dofusdude_json_fr = open("input/dofusdude/equipment/fr_all.json")
    fr_dofusdude_data = json.load(dofusdude_json_fr)
    dofusdude_json_fr.close()

    dofusdude_json_es = open("input/dofusdude/equipment/es_all.json")
    es_dofusdude_data = json.load(dofusdude_json_es)
    dofusdude_json_es.close()

    dofusdude_json_pt = open("input/dofusdude/equipment/pt_all.json")
    pt_dofusdude_data = json.load(dofusdude_json_pt)
    dofusdude_json_pt.close()

    dofusdude_json_de = open("input/dofusdude/equipment/de_all.json")
    de_dofusdude_data = json.load(dofusdude_json_de)
    dofusdude_json_de.close()

    dofusdude_json_it = open("input/dofusdude/equipment/it_all.json")
    it_dofusdude_data = json.load(dofusdude_json_it)
    dofusdude_json_it.close()

    # sort for convenience and consistency of output:
    en_dofusdude_data["items"] = sorted(en_dofusdude_data["items"], key=lambda k: k["ankama_id"])
    fr_dofusdude_data["items"] = sorted(fr_dofusdude_data["items"], key=lambda k: k["ankama_id"])
    es_dofusdude_data["items"] = sorted(es_dofusdude_data["items"], key=lambda k: k["ankama_id"])
    de_dofusdude_data["items"] = sorted(de_dofusdude_data["items"], key=lambda k: k["ankama_id"])
    it_dofusdude_data["items"] = sorted(it_dofusdude_data["items"], key=lambda k: k["ankama_id"])
    pt_dofusdude_data["items"] = sorted(pt_dofusdude_data["items"], key=lambda k: k["ankama_id"])

    dofusdude_data = {}
    dofusdude_data["en"] = en_dofusdude_data
    dofusdude_data["fr"] = fr_dofusdude_data
    dofusdude_data["es"] = es_dofusdude_data
    dofusdude_data["de"] = de_dofusdude_data
    dofusdude_data["it"] = it_dofusdude_data
    dofusdude_data["pt"] = pt_dofusdude_data

    # All DofusLab data to be compiled together
    dofuslab_data = {}

    dofuslab_data["items"] = []
    dofuslab_data["mounts"] = []
    dofuslab_data["pets"] = []
    dofuslab_data["rhineetles"] = []
    dofuslab_data["weapons"] = []

    if not args.ignore_dofuslab:
        # Opens all Dofuslab data files and aggregates them
        dofuslab_current_items = open("input/dofuslab/items.json", "r")
        current_dl_items = json.load(dofuslab_current_items)
        dofuslab_current_items.close()

        dofuslab_current_mounts = open("input/dofuslab/mounts.json", "r")
        current_dl_mounts = json.load(dofuslab_current_mounts)
        dofuslab_current_mounts.close()

        dofuslab_current_pets = open("input/dofuslab/pets.json", "r")
        current_dl_pets = json.load(dofuslab_current_pets)
        dofuslab_current_pets.close()

        dofuslab_current_rhineetles = open("input/dofuslab/rhineetles.json", "r")
        current_dl_rhineetles = json.load(dofuslab_current_rhineetles)
        dofuslab_current_rhineetles.close()

        dofuslab_current_weapons = open("input/dofuslab/weapons.json", "r")
        current_dl_weapons = json.load(dofuslab_current_weapons)
        dofuslab_current_weapons.close()

        dofuslab_data["items"] = current_dl_items
        dofuslab_data["mounts"] = current_dl_mounts
        dofuslab_data["pets"] = current_dl_pets
        dofuslab_data["rhineetles"] = current_dl_rhineetles
        dofuslab_data["weapons"] = current_dl_weapons

    transform_items(
        dofusdude_data, dofuslab_data, skip=args.skip, replace=args.replace, download_imgs=args.download_imgs
    )


if __name__ == "__main__":
    main()
