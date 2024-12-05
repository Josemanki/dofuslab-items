#!/usr/bin/env python3

from os import path, makedirs
import json
import argparse
import logging
import coloredlogs
import re
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
        logger.info(f"Added:  {item['name']['en']} to pets")

    elif item["itemType"] in WEAPON_TYPES:
        data["weapons"].append(item)
        logger.info(f"Added:  {item['name']['en']} to weapons")

    elif item["itemType"] == "Mount" and item["name"]["en"].contains("Rhineetle"):
        data["rhineetles"].append(item)
        logger.info(f"Added:  {item['name']['en']} to rhineetles")

    elif item["itemType"] == "Mount":
        data["mounts"].append(item)
        logger.info(f"Added:  {item['name']['en']} to mounts")

    else:
        # itemType can be "Cloak", etc
        data["items"].append(item)
        logger.info(f"Added:  {item['name']['en']} to items")


def format_image(image_urls):
    # return image_urls["sd"].split("item/")[1]
    full_name = "item/" + image_urls["icon"].split("item/")[1]
    # ex: "item/1005-64.png"
    name_stripped = re.sub("-\\d+", "", full_name)
    # ex: "item/1005.png"
    return name_stripped


def format_image_and_download(image_urls):
    dir_path = path.dirname(path.realpath(__file__))
    img_id_with_size = image_urls["sd"].split("item/")[1]
    img_id = re.sub("-\\d+", "", img_id_with_size)
    subfolder = "output/images"
    complete_name = path.join(dir_path, subfolder, img_id)
    img_data = requests.get(image_urls["sd"]).content

    if not path.exists(path.join(dir_path, subfolder)):
        makedirs(path.join(dir_path, subfolder))

    with open(complete_name, "wb") as handler:
        handler.write(img_data)
    return img_id


def transform_conditions(conditions: dict) -> dict:
    """
    Survival changed how he formats conditions and now there's a "condition_tree"
    that this doesn't handle. As such, this will probably go away in favor of
    handling the tree.
    """
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


def transform_condition(condition: dict) -> dict:
    """
    Transforms a single condition to the DofusLab style from Doduda
    """
    dofuslab_condition = {
        "stat": condition["element"]["name"].upper().replace(" ", "_"),
        "operator": condition["operator"],
        "value": condition["int_value"],
    }
    return dofuslab_condition


def transform_cond_subtree(tree: dict) -> dict:
    """
    If this 'is_operand' then it has a 'condition' with stats
    Otherwise, it has 'children' and a 'relation' and we should recurse.
    """
    ret_dict = {}
    conditions = []
    relation = tree["relation"]
    for child in tree["children"]:
        if child["is_operand"]:
            conditions.append(transform_condition(child["condition"]))
        else:
            conditions.append(transform_cond_subtree(child))

    ret_dict[relation] = conditions

    # note: we need to flatten the tree if there's multiple nested
    # relations of the same type, as doduda just does 2 per "and"/"or"
    # but dofuslab can string many children under the same comparison
    # together

    # flatten the tree before returning it to the stack:
    for child in ret_dict[relation]:
        # check if the child has the same operator as above:
        if relation in child:
            # flatten
            for stat in child[relation]:
                ret_dict[relation].append(stat)
            ret_dict[relation].remove(child)

    return ret_dict


def transform_condition_tree(condition_tree: dict) -> dict:
    """
    Tempted to handle this tree recursively because I'm too tired to
     do it iteratively, and the tree should only be like max 2 depth
    """
    dofuslab_conditions = {}

    dofuslab_conditions["conditions"] = {}
    dofuslab_conditions["customConditions"] = {}  # todo: fill these out when the API supports it

    # handle the base case:
    if condition_tree["is_operand"]:
        dofuslab_conditions["conditions"] = transform_condition(condition_tree["condition"])
    else:
        # there's a `relation` here that corresponds to a key in the
        # dofuslab data structure, and a `children` that has the conditions that
        # correspond to the tree off of that relation
        dofuslab_conditions["conditions"] = transform_cond_subtree(condition_tree)

    return dofuslab_conditions


def transform_stats(stats: dict) -> dict:
    normal_stats = []
    weapon_stats = []
    # custom_stats = {"en": [], "fr": [], "de": [], "es": [], "it": [], "pt": []}
    custom_stats = {"en": [], "fr": [], "de": [], "es": [], "pt": []}

    for stat in stats:
        ## API ID for -AP is 179 and -MP is 192 - these are weapon stats only
        ## AP and MP for items are correctly handled in the mappings below.
        if stat["type"]["id"] == 179 or stat["type"]["id"] == 192:
            weapon_stats.append(
                {
                    "stat": stat["type"]["name"],
                    "minStat": (stat["int_minimum"] if stat["int_maximum"] != 0 else None),
                    "maxStat": (stat["int_maximum"] if stat["int_maximum"] != 0 else stat["int_minimum"]),
                }
            )
        elif stat["type"]["name"] in NORMAL_STAT_MAP:
            normal_stats.append(
                {
                    "stat": NORMAL_STAT_MAP[stat["type"]["name"]],
                    "minStat": (stat["int_minimum"] if stat["int_maximum"] != 0 else None),
                    "maxStat": (stat["int_maximum"] if stat["int_maximum"] != 0 else stat["int_minimum"]),
                }
            )
        elif stat["type"]["name"] in WEAPON_STAT_MAP:
            weapon_stats.append(
                {
                    "stat": WEAPON_STAT_MAP[stat["type"]["name"]],
                    "minStat": (stat["int_minimum"] if stat["int_maximum"] != 0 else None),
                    "maxStat": (stat["int_maximum"] if stat["int_maximum"] != 0 else stat["int_minimum"]),
                }
            )
        elif stat["type"]["name"] in CUSTOM_STAT_MAP:
            custom_stats["en"].append(stat["formatted"])
            custom_stats["fr"].append(stat["type"]["id"])
            custom_stats["de"].append(stat["type"]["id"])
            custom_stats["es"].append(stat["type"]["id"])
            custom_stats["pt"].append(stat["type"]["id"])
            # custom_stats["it"].append(stat["type"]["id"])

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


def localize_custom_stats_from_item(en_item, item):
    custom_stats = []

    for effect in zip(en_item["effects"], item["effects"]):
        if effect[0]["type"]["name"] in NORMAL_STAT_MAP:
            continue

        # if it's not in the normal stat map, it's *probably* something
        #  that we want to include, but there's a couple examples of stuff
        #  that we don't want to include:
        # - Exchangable: 0
        # - Emote: 0
        # note: they seem to be somewhat inconsistently typed, might be something
        #  Survival has control over.
        # so, let's filter these out:
        if effect[0]["type"]["name"] in ["Exchangeable:", "emote", "Emote"]:
            continue

        # apparently we also need to filter out damage lines on weapons:
        if " damage)" in effect[0]["type"]["name"]:
            continue
        if " steal)" in effect[0]["type"]["name"]:
            continue

        custom_stats.append(effect[1]["formatted"])

    return custom_stats


def get_dofuslab_titles_for_item(item_id, data_block, dofuslab_data):
    # ret_titles = {"en": "", "fr": "", "de": "", "es": "", "it": "", "pt": ""}
    ret_titles = {"en": "", "fr": "", "de": "", "es": "", "pt": ""}

    # langs = ["en", "fr", "de", "es", "it", "pt"]
    langs = ["en", "fr", "de", "es", "pt"]
    title_name = {
        "en": "Title",
        "fr": "Titre",
        "de": "Titel",
        "es": "Título",
        "pt": "Título",
        # "it": "Titolo",
    }

    for item in dofuslab_data[data_block]:
        if int(item["dofusID"]) == item_id:
            # sometimes we just don't have the title in the old data. In that case,
            #  let's just remove the title.
            if item["customStats"] == {}:
                break
            if isinstance(item["customStats"], list):
                # for some reason, sometimes this is a list, not a dict?
                break

            # find the title within the custom stats, using our title_name to search
            for lang in langs:
                for entry in item["customStats"][lang]:
                    if title_name[lang] in entry:
                        ret_titles[lang] = entry
                        break
            # will break out of the inner loop, onto searching the next localization's data:
            break

    return ret_titles


def get_dofuslab_customConditions_for_item(item_id, data_block, dofuslab_data):
    """
    This is for importing customConditions from old DofusLab data since Survival's API
    currently doesn't support them.
    """
    for item in dofuslab_data[data_block]:
        if int(item["dofusID"]) == item_id:
            if item["conditions"]["customConditions"] == {}:
                return {}

            # Copy over the customConditions wholesale:
            return item["conditions"]["customConditions"]

    # if it isn't found, return {}
    return {}


def transform_items(
    dofusdude_data,
    dofuslab_data,
    skip=True,
    replace=False,
    download_imgs=False,
    import_titles=False,
    import_custom_conditions=False,
):
    # set up dictionary of lists of items
    my_data = {}
    for item_type in {"items", "mounts", "pets", "rhineetles", "weapons"}:
        my_data[item_type] = []

    # make the output path in case it doesn't exist:
    if not path.exists("output"):
        makedirs("output")

    for item in dofusdude_data["en"]["items"]:
        if item["name"] == "Hat Ariutokinabot":
            print("break!")

        if skip and item_exists(item["name"], dofuslab_data):
            logger.info(f"Skipping: {item['name']}")
            continue
        elif replace and item_exists(item["name"], dofuslab_data):
            remove_item(item["name"], dofuslab_data)
        elif item["type"]["name"] in IGNORED_ITEM_TYPES:
            logger.info(f"Skipping: {item['name']}")
            continue
        elif item["ankama_id"] in IGNORED_ITEM_IDS:
            logger.info(f"Skipping: {item['name']}")
            continue
        elif item["is_weapon"]:
            # WEAPON TRANSFORMATION
            # if "effects" in item and item["type"]["name"] not in IGNORED_CATEGORIES:
            if "effects" not in item or item["type"]["name"] in IGNORED_CATEGORIES:
                continue

            logger.debug(f"Adding: {item['name']}")
            item_effects = transform_stats(item["effects"])
            custom_stats = {}

            # Locales
            en_item = find_localized_item(item["ankama_id"], dofusdude_data["en"]["items"])
            fr_item = find_localized_item(item["ankama_id"], dofusdude_data["fr"]["items"])
            es_item = find_localized_item(item["ankama_id"], dofusdude_data["es"]["items"])
            de_item = find_localized_item(item["ankama_id"], dofusdude_data["de"]["items"])
            pt_item = find_localized_item(item["ankama_id"], dofusdude_data["pt"]["items"])
            # it_item = find_localized_item(
            #     item["ankama_id"], dofusdude_data["it"]["items"]
            # )

            if "en" in item_effects["customStats"]:
                custom_stats = {
                    "en": item_effects["customStats"]["en"],
                    "fr": localize_custom_stats_from_item(en_item, fr_item),
                    "de": localize_custom_stats_from_item(en_item, de_item),
                    "es": localize_custom_stats_from_item(en_item, es_item),
                    "pt": localize_custom_stats_from_item(en_item, pt_item),
                    # "it": localize_custom_stats_from_item(en_item, it_item),
                }

            rebuilt_item = {
                # this needs to be a str, but for the purposes of sorting, we'll make it an int
                # and convert it to a str later.
                "dofusID": item["ankama_id"],
                "name": {
                    "en": en_item["name"],
                    "fr": fr_item["name"],
                    "de": de_item["name"],
                    "es": es_item["name"],
                    "pt": pt_item["name"],
                    # "it": it_item["name"],
                },
                "itemType": item["type"]["name"],
                "setID": (str(item["parent_set"]["id"]) if "parent_set" in item else None),
                "level": item["level"],
                "stats": item_effects["stats"],
                "weaponStats": {
                    "apCost": item["ap_cost"],
                    "usesPerTurn": item["max_cast_per_turn"],
                    "minRange": (item["range"]["min"] if item["range"]["min"] != item["range"]["max"] else None),
                    "maxRange": item["range"]["max"],
                    "baseCritChance": item["critical_hit_probability"],
                    "critBonusDamage": item["critical_hit_bonus"],
                    "weapon_effects": item_effects["weaponStats"],
                },
                "customStats": custom_stats,
                # "conditions": transform_conditions(item["conditions"])
                # if "conditions" in item
                # else {"conditions": {}, "customConditions": {}},
                "conditions": (
                    transform_condition_tree(item["condition_tree"])
                    if "condition_tree" in item
                    else {"conditions": {}, "customConditions": {}}
                ),
                "imageUrl": format_image(item["image_urls"]),
            }
            categorize_item(rebuilt_item, my_data)
            if download_imgs:
                format_image_and_download(item["image_urls"])
        else:
            # ITEM TRANSFORMATION
            # if "effects" in item and item["type"]["name"] not in IGNORED_CATEGORIES:
            if "effects" not in item or item["type"]["name"] in IGNORED_CATEGORIES:
                continue

            logger.debug(f"Adding: {item['name']}")
            item_effects = transform_stats(item["effects"])
            custom_stats = {}

            # Locales
            en_item = find_localized_item(item["ankama_id"], dofusdude_data["en"]["items"])
            fr_item = find_localized_item(item["ankama_id"], dofusdude_data["fr"]["items"])
            es_item = find_localized_item(item["ankama_id"], dofusdude_data["es"]["items"])
            de_item = find_localized_item(item["ankama_id"], dofusdude_data["de"]["items"])
            pt_item = find_localized_item(item["ankama_id"], dofusdude_data["pt"]["items"])
            # it_item = find_localized_item(
            #     item["ankama_id"], dofusdude_data["it"]["items"]
            # )

            if "en" in item_effects["customStats"]:
                custom_stats = {
                    "en": item_effects["customStats"]["en"],
                    "fr": localize_custom_stats_from_item(en_item, fr_item),
                    "de": localize_custom_stats_from_item(en_item, de_item),
                    "es": localize_custom_stats_from_item(en_item, es_item),
                    "pt": localize_custom_stats_from_item(en_item, pt_item),
                    # "it": localize_custom_stats_from_item(en_item, it_item),
                }

            rebuilt_item = {
                # this needs to be a str, but for the purposes of sorting, we'll make it an int
                # and convert it to a str later.
                "dofusID": item["ankama_id"],
                "name": {
                    "en": en_item["name"],
                    "fr": fr_item["name"],
                    "de": de_item["name"],
                    "es": es_item["name"],
                    "pt": pt_item["name"],
                    # "it": it_item["name"],
                },
                "itemType": item["type"]["name"],
                "setID": (str(item["parent_set"]["id"]) if "parent_set" in item else None),
                "level": item["level"],
                "stats": item_effects["stats"],
                "customStats": custom_stats,
                # "conditions": transform_conditions(item["conditions"])
                # if "conditions" in item
                # else {"conditions": {}, "customConditions": {}},
                "conditions": (
                    transform_condition_tree(item["condition_tree"])
                    if "condition_tree" in item
                    else {"conditions": {}, "customConditions": {}}
                ),
                "imageUrl": format_image(item["image_urls"]),
            }
            categorize_item(rebuilt_item, my_data)
            if download_imgs:
                format_image_and_download(item["image_urls"])

    # more processing to remove extra conditions on pets:
    logger.info("Cleaning up conditions on pets...")
    for item in my_data["pets"]:
        # for some reason, we have a "= 0" condition on our petsmounts
        conds_to_remove = {
            "conditions": {"and": [{"stat": "", "operator": "=", "value": 1}]},
            "customConditions": {},
        }
        # remove it:
        if item["conditions"] == conds_to_remove:
            logger.info(f"Removing extraneous conditions on {item['name']['en']}")
            item["conditions"] = {"conditions": {}, "customConditions": {}}

    # copy stuff over from dofuslab data for items that grant titles:
    # note: this has since been fixed in the API
    if import_titles:
        logger.info("Fixing titles...")
        localizations = ["en", "fr", "de", "es", "it", "pt"]
        title_localizations = {
            "en": "Title: 0",
            "fr": "Titre : 0",
            "de": "Titel: 0",
            "it": "Titolo: 0",
            "es": "Título: 0.",
            "pt": "Título: 0",
        }
        for data_block in my_data:
            for item in my_data[data_block]:
                # find items with titles:
                if item["customStats"] != {} and "Title: 0" in item["customStats"]["en"]:
                    # go find the appropriate title from DofusLab's data
                    titles = get_dofuslab_titles_for_item(item["dofusID"], data_block, dofuslab_data)

                    # remove the old "Title: 0" (etc) titles:
                    for lang in localizations:
                        item["customStats"][lang].remove(title_localizations[lang])

                    # add the title to our stats:
                    for lang in localizations:
                        if titles[lang] != "":
                            item["customStats"][lang].append(titles[lang])

    # copy stuff over from dofuslab data for items that have custom (typically quest) conditions:
    if import_custom_conditions:
        logger.info("Fixing custom conditions...")
        for data_block in my_data:
            for item in my_data[data_block]:
                item["conditions"]["customConditions"] = get_dofuslab_customConditions_for_item(
                    item["dofusID"], data_block, dofuslab_data
                )

    # sort items and change the dofusIDs to strings, since that's apparently load-bearing
    logger.info("Sorting items and converting IDs to strings...")
    for data_block in my_data:
        my_data[data_block] = sorted(my_data[data_block], key=lambda d: d["dofusID"])

        for item in my_data[data_block]:
            item["dofusID"] = str(item["dofusID"])

    logger.info("Writing files...")
    # write our files:
    with open("output/items.json", "w", encoding="utf8") as outfile:
        outfile.write(json.dumps(my_data["items"], indent=4, ensure_ascii=False))
        outfile.close()

    # this doesn't currently populate
    # with open("output/mounts.json", "w+", encoding="utf8") as outfile:
    #     outfile.write(json.dumps(final_data["mounts"], indent=2, ensure_ascii=False))
    #     outfile.close()

    with open("output/pets.json", "w", encoding="utf8") as outfile:
        outfile.write(json.dumps(my_data["pets"], indent=4, ensure_ascii=False))
        outfile.close()

    # this doesn't currently populate, so skip writing it
    # with open("output/rhineetles.json", "w+", encoding="utf8") as outfile:
    #     outfile.write(json.dumps(dofuslab_data["rhineetles"] + final_data["rhineetles"], indent=2, ensure_ascii=False))
    #     outfile.close()

    with open("output/weapons.json", "w", encoding="utf8") as outfile:
        outfile.write(json.dumps(my_data["weapons"], indent=4, ensure_ascii=False))
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
        "-v",
        "--verbose",
        action="store_true",
        help="Enables verbose debug output",
        default=False,
    )
    parser.add_argument(
        "-d",
        "--download_imgs",
        action="store_true",
        help="Downloads images from doduda for items",
        default=False,
    )
    parser.add_argument(
        "-t",
        "--import_dofuslab_titles",
        action="store_true",
        help="Overwrites titles with data from DofusLab",
        default=False,
    )
    parser.add_argument(
        "-c",
        "--import_dofuslab_custom_conditions",
        action="store_true",
        help="Overwrites custom conditions with data from DofusLab",
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
    dofusdude_data["pt"] = pt_dofusdude_data
    # dofusdude_data["it"] = it_dofusdude_data

    # All DofusLab data to be compiled together
    dofuslab_data = {}

    # Opens all Dofuslab data files and aggregates them
    dofuslab_current_items = open("input/dofuslab/items.json", "r")
    dofuslab_data["items"] = json.load(dofuslab_current_items)
    dofuslab_current_items.close()

    dofuslab_current_mounts = open("input/dofuslab/mounts.json", "r")
    dofuslab_data["mounts"] = json.load(dofuslab_current_mounts)
    dofuslab_current_mounts.close()

    dofuslab_current_pets = open("input/dofuslab/pets.json", "r")
    dofuslab_data["pets"] = json.load(dofuslab_current_pets)
    dofuslab_current_pets.close()

    dofuslab_current_rhineetles = open("input/dofuslab/rhineetles.json", "r")
    dofuslab_data["rhineetles"] = json.load(dofuslab_current_rhineetles)
    dofuslab_current_rhineetles.close()

    dofuslab_current_weapons = open("input/dofuslab/weapons.json", "r")
    dofuslab_data["weapons"] = json.load(dofuslab_current_weapons)
    dofuslab_current_weapons.close()

    # for some reason, some of the IDs are strs, and some are ints.
    # convert ids to int:
    for category in dofuslab_data:
        for item in dofuslab_data[category]:
            item["dofusID"] = int(item["dofusID"])

    # sort em for convenience:
    dofuslab_data["items"] = sorted(dofuslab_data["items"], key=lambda k: k["dofusID"])
    dofuslab_data["mounts"] = sorted(dofuslab_data["mounts"], key=lambda k: k["dofusID"])
    dofuslab_data["pets"] = sorted(dofuslab_data["pets"], key=lambda k: k["dofusID"])
    dofuslab_data["rhineetles"] = sorted(dofuslab_data["rhineetles"], key=lambda k: k["dofusID"])
    dofuslab_data["weapons"] = sorted(dofuslab_data["weapons"], key=lambda k: k["dofusID"])

    # convert ids back to str:
    for category in dofuslab_data:
        for item in dofuslab_data[category]:
            item["dofusID"] = int(item["dofusID"])

    transform_items(
        dofusdude_data,
        dofuslab_data,
        skip=args.skip,
        replace=args.replace,
        download_imgs=args.download_imgs,
        import_titles=args.import_dofuslab_titles,
        import_custom_conditions=args.import_dofuslab_custom_conditions,
    )


if __name__ == "__main__":
    main()
