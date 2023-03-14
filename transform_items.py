from os import path
import json
import requests
from constants import CUSTOM_STAT_MAP, NORMAL_STAT_MAP, PET_ITEM_TYPES, WEAPON_TYPES, WEAPON_STAT_MAP, IGNORED_CATEGORIES

# Opening all languages in order to populate localized names
# This will be a list of requests in the future, not so many files being opened

dofusdude_json_en = open(
    'input/dofusdude/equipment/en_all.json')
en_dofusdude_data = json.load(dofusdude_json_en)
dofusdude_json_en.close()

dofusdude_json_fr = open(
    'input/dofusdude/equipment/fr_all.json')
fr_dofusdude_data = json.load(dofusdude_json_fr)
dofusdude_json_fr.close()

dofusdude_json_es = open(
    'input/dofusdude/equipment/es_all.json')
es_dofusdude_data = json.load(dofusdude_json_es)
dofusdude_json_es.close()

dofusdude_json_pt = open(
    'input/dofusdude/equipment/pt_all.json')
pt_dofusdude_data = json.load(dofusdude_json_pt)
dofusdude_json_pt.close()

dofusdude_json_de = open(
    'input/dofusdude/equipment/de_all.json')
de_dofusdude_data = json.load(dofusdude_json_de)
dofusdude_json_de.close()

dofusdude_json_it = open(
    'input/dofusdude/equipment/it_all.json')
it_dofusdude_data = json.load(dofusdude_json_it)
dofusdude_json_it.close()

# All DofusLab data to be compiled together
dofuslab_full_data = []

# Opens all Dofuslab data files and aggregates them
dofuslab_current_items = open(
    'input/dofuslab/items.json', 'r')
serialized_current_items = json.load(dofuslab_current_items)
dofuslab_current_items.close()

dofuslab_current_mounts = open(
    'input/dofuslab/mounts.json', 'r')
serialized_current_mounts = json.load(
    dofuslab_current_mounts)
dofuslab_current_mounts.close()

dofuslab_current_pets = open(
    'input/dofuslab/pets.json', 'r')
serialized_current_pets = json.load(dofuslab_current_pets)
dofuslab_current_pets.close()

dofuslab_current_rhineetles = open(
    'input/dofuslab/rhineetles.json', 'r')
serialized_current_rhineetles = json.load(
    dofuslab_current_rhineetles)
dofuslab_current_rhineetles.close()

dofuslab_current_weapons = open(
    'input/dofuslab/weapons.json', 'r')
serialized_current_weapons = json.load(
    dofuslab_current_weapons)
dofuslab_current_weapons.close()

dofuslab_full_data = serialized_current_items + serialized_current_mounts + \
    serialized_current_pets + serialized_current_rhineetles + \
    serialized_current_weapons

# Maps everything to their json file
final_items = []
final_weapons = []
final_mounts = []
final_rhineetles = []
final_pets = []


def item_exists(name):
  for i in dofuslab_full_data:
    if i['name']['en'] == name:
      return True


def categorize_item(item):
  if item['itemType'] in PET_ITEM_TYPES:
    final_pets.append(item)
  elif item['itemType'] in WEAPON_TYPES:
    final_weapons.append(item)
  elif item['itemType'] == 'Mount' and item['name']['en'].contains('Rhineetle'):
    final_rhineetles.append(item)
  elif item['itemType'] == 'Mount':
    final_mounts.append(item)
  else:
    final_items.append(item)


def format_image_and_download(image_urls):
  dir_path = path.dirname(path.realpath(__file__))
  img_id = image_urls['icon'].split('item/')[1]
  subfolder = "output/images"
  complete_name = path.join(dir_path, subfolder, img_id)
  img_data = requests.get(image_urls['icon']).content
  with open(complete_name, 'wb') as handler:
    handler.write(img_data)
  return img_id


def transform_conditions(conditions):
  condition_list = {
      'and': []
  }
  for condition in conditions:
    condition_list['and'].append({
        'stat': condition['element']['name'].upper().replace(' ', '_'),
        'operator': condition['operator'],
        'value': condition['int_value']
    })
  return condition_list


def transform_stats(stats):
  normal_stats = []
  weapon_stats = []
  custom_stats = {'en': [], 'fr': [],
                  'de': [], 'es': [], 'it': [], 'pt': []}

  for stat in stats:
    if stat['type']['name'] in NORMAL_STAT_MAP:
      normal_stats.append({
          'stat': NORMAL_STAT_MAP[stat['type']['name']],
          'minStat': stat['int_minimum'] if stat['int_maximum'] != 0 else None,
          'maxStat': stat['int_maximum'] if stat['int_maximum'] != 0 else stat['int_minimum']
      })
    elif stat['type']['name'] in WEAPON_STAT_MAP:
      weapon_stats.append({
          'stat': WEAPON_STAT_MAP[stat['type']['name']],
          'minStat': stat['int_minimum'] if stat['int_maximum'] != 0 else None,
          'maxStat': stat['int_maximum'] if stat['int_maximum'] != 0 else stat['int_minimum']
      })
    elif stat['type']['name'] in CUSTOM_STAT_MAP:
      custom_stats['en'].append(stat['formatted'])
      custom_stats['fr'].append(stat['type']['id'])
      custom_stats['de'].append(stat['type']['id'])
      custom_stats['es'].append(stat['type']['id'])
      custom_stats['it'].append(stat['type']['id'])
      custom_stats['pt'].append(stat['type']['id'])

  return {
      'stats': normal_stats,
      'weaponStats': weapon_stats,
      'customStats': custom_stats if len(custom_stats['en']) > 0 else {}
  }


def find_localized_item(item_id, language_data):
  try:
    found = next(
        item for item in language_data if item["ankama_id"] == item_id)
    return found
  except StopIteration:
    print('Not found!')


def localize_custom_stats_from_id(stat_ids, item_stats):
  custom_stats = []

  for stat_id in stat_ids:
    found = next(
        item for item in item_stats if item['type']['id'] == stat_id)
    custom_stats.append(found['formatted'])

  return custom_stats


def transform_items():

  for item in en_dofusdude_data:
    if item_exists(item['name']):
      continue
    elif item['is_weapon']:
      # WEAPON TRANSFORMATION
      if 'effects' in item and item['type']['name'] not in IGNORED_CATEGORIES:
        print('Adding {} to items...'.format(item['name']))
        item_effects = transform_stats(item['effects'])
        custom_stats = {}

        # Locales
        en_item = find_localized_item(
            item['ankama_id'], en_dofusdude_data)
        fr_item = find_localized_item(
            item['ankama_id'], fr_dofusdude_data)
        es_item = find_localized_item(
            item['ankama_id'], es_dofusdude_data)
        de_item = find_localized_item(
            item['ankama_id'], de_dofusdude_data)
        it_item = find_localized_item(
            item['ankama_id'], it_dofusdude_data)
        pt_item = find_localized_item(
            item['ankama_id'], pt_dofusdude_data)

        if ('en' in item_effects['customStats']):
          custom_stats = {
              'en': item_effects['customStats']['en'],
              'fr': localize_custom_stats_from_id(item_effects['customStats']['fr'], fr_item['effects']),
              'de': localize_custom_stats_from_id(item_effects['customStats']['de'], de_item['effects']),
              'it': localize_custom_stats_from_id(item_effects['customStats']['it'], it_item['effects']),
              'es': localize_custom_stats_from_id(item_effects['customStats']['es'], es_item['effects']),
              'pt': localize_custom_stats_from_id(item_effects['customStats']['pt'], pt_item['effects'])
          }

        rebuilt_item = {
            'dofusID': str(item['ankama_id']),
            'name': {
                'en': en_item['name'],
                'fr': fr_item['name'],
                'de': de_item['name'],
                'it': it_item['name'],
                'es': es_item['name'],
                'pt': pt_item['name']
            },
            'itemType': item['type']['name'],
            'setID': item['parent_set']['id'] if 'parent_set' in item else None,
            'level': item['level'],
            'stats': item_effects['stats'],
            'weaponStats': {
                'apCost': item['ap_cost'],
                'usesPerTurn': item['max_cast_per_turn'],
                "minRange": item['range']['min'] if item['range']['min'] != item['range']['max'] else None,
                "maxRange": item['range']['max'],
                "baseCritChance": item['critical_hit_probability'],
                "critBonusDamage": item['critical_hit_bonus'],
                'weapon_effects': item_effects['weaponStats']
            },
            'customStats': custom_stats,
            'conditions': transform_conditions(item['conditions']) if 'conditions' in item else {},
            'image': format_image_and_download(item['image_urls'])
        }
        categorize_item(rebuilt_item)
        print('Added {} to items'.format(item['name']))
    else:
      # ITEM TRANSFORMATION
      if 'effects' in item and item['type']['name'] not in IGNORED_CATEGORIES:
        print('Adding {} to items...'.format(item['name']))
        item_effects = transform_stats(item['effects'])
        custom_stats = {}

        # Locales
        en_item = find_localized_item(
            item['ankama_id'], en_dofusdude_data)
        fr_item = find_localized_item(
            item['ankama_id'], fr_dofusdude_data)
        es_item = find_localized_item(
            item['ankama_id'], es_dofusdude_data)
        de_item = find_localized_item(
            item['ankama_id'], de_dofusdude_data)
        it_item = find_localized_item(
            item['ankama_id'], it_dofusdude_data)
        pt_item = find_localized_item(
            item['ankama_id'], pt_dofusdude_data)

        if ('en' in item_effects['customStats']):
          custom_stats = {
              'en': item_effects['customStats']['en'],
              'fr': localize_custom_stats_from_id(item_effects['customStats']['fr'], fr_item['effects']),
              'de': localize_custom_stats_from_id(item_effects['customStats']['de'], de_item['effects']),
              'it': localize_custom_stats_from_id(item_effects['customStats']['it'], it_item['effects']),
              'es': localize_custom_stats_from_id(item_effects['customStats']['es'], es_item['effects']),
              'pt': localize_custom_stats_from_id(item_effects['customStats']['pt'], pt_item['effects'])
          }

        rebuilt_item = {
            'dofusID': str(item['ankama_id']),
            'name': {
                'en': en_item['name'],
                'fr': fr_item['name'],
                'de': de_item['name'],
                'it': it_item['name'],
                'es': es_item['name'],
                'pt': pt_item['name']
            },
            'itemType': item['type']['name'],
            'setID': item['parent_set']['id'] if 'parent_set' in item else None,
            'level': item['level'],
            'stats': item_effects['stats'],
            'customStats': custom_stats,
            'conditions': transform_conditions(item['conditions']) if 'conditions' in item else {},
            'image': format_image_and_download(item['image_urls'])
        }
        categorize_item(rebuilt_item)
        print('Added {} to items'.format(item['name']))

    with open('output/items.json', 'w+', encoding='utf8') as outfile:
      outfile.write(json.dumps(serialized_current_items +
                    final_items, ensure_ascii=False))
      outfile.close()

    with open('output/mounts.json', 'w+', encoding='utf8') as outfile:
      outfile.write(json.dumps(serialized_current_mounts +
                    final_mounts, ensure_ascii=False))
      outfile.close()

    with open('output/pets.json', 'w+', encoding='utf8') as outfile:
      outfile.write(json.dumps(serialized_current_pets +
                    final_pets, ensure_ascii=False))
      outfile.close()

    with open('output/rhineetles.json', 'w+', encoding='utf8') as outfile:
      outfile.write(json.dumps(
          serialized_current_rhineetles + final_rhineetles, ensure_ascii=False))
      outfile.close()

    with open('output/weapons.json', 'w+', encoding='utf8') as outfile:
      outfile.write(json.dumps(serialized_current_weapons +
                    final_weapons, ensure_ascii=False))
      outfile.close()


__main__ = transform_items()
