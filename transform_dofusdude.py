from os import path
import json
import requests
from constants import CUSTOM_STAT_MAP, NORMAL_STAT_MAP, PET_ITEM_TYPES, WEAPON_TYPES

dofusdude_data = open('input/dofusdude-example-2.json')
serialized = json.load(dofusdude_data)
dofusdude_data.close()

# All DofusLab data compiled together
dofuslab_full_data = []

# Opens all Dofuslab data files
dofuslab_current_items = open('input/items.json', 'r')
serialized_current_items = json.load(dofuslab_current_items)
dofuslab_current_items.close()

dofuslab_current_mounts = open('input/mounts.json', 'r')
serialized_current_mounts = json.load(dofuslab_current_mounts)
dofuslab_current_mounts.close()

dofuslab_current_pets = open('input/pets.json', 'r')
serialized_current_pets = json.load(dofuslab_current_pets)
dofuslab_current_pets.close()

dofuslab_current_rhineetles = open('input/rhineetles.json', 'r')
serialized_current_rhineetles = json.load(dofuslab_current_rhineetles)
dofuslab_current_rhineetles.close()

dofuslab_current_weapons = open('input/weapons.json', 'r')
serialized_current_weapons = json.load(dofuslab_current_weapons)
dofuslab_current_weapons.close()

dofuslab_full_data = serialized_current_items + serialized_current_mounts + \
    serialized_current_pets + serialized_current_rhineetles + serialized_current_weapons

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
  # dir_path = path.dirname(path.realpath(__file__))
  img_id = image_urls['icon'].split('item/')[1]
  # subfolder = "output/images"
  # complete_name = path.join(dir_path, subfolder, img_id)
  # img_data = requests.get(image_urls['icon']).content
  # with open(complete_name, 'wb') as handler:
  #   handler.write(img_data)
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
  custom_stats = {'en': [], 'fr': [], 'de': [], 'es': [], 'it': [], 'pt': []}

  for stat in stats:
    if stat['type']['name'] in NORMAL_STAT_MAP:
      normal_stats.append({
          'stat': stat['type']['name'],
          'minStat': stat['int_minimum'] if stat['int_maximum'] != 0 else None,
          'maxStat': stat['int_maximum'] if stat['int_maximum'] != 0 else stat['int_minimum']
      })
    elif stat['type']['name'] in CUSTOM_STAT_MAP:
      custom_stats['en'].append(stat['formatted'])
      custom_stats['fr'].append(stat['formatted'])
      custom_stats['de'].append(stat['formatted'])
      custom_stats['es'].append(stat['formatted'])
      custom_stats['it'].append(stat['formatted'])
      custom_stats['pt'].append(stat['formatted'])
  return {
      'stats': normal_stats,
      'customStats': custom_stats if len(custom_stats['en']) > 0 else {}
  }


def transform_items():
  ignored_categories = ['Sidekick', 'Tool',
                        'Pickaxe', 'Soul stone', 'Capturing net', 'Prysmaradite', 'Magic weapon', 'Expedition Idol']

  for item in serialized:
    if item_exists(item['name']):
      print('{} is already in the list'.format(item['name']))
    else:
      if 'effects' in item and item['type']['name'] not in ignored_categories:
        print('Adding {} to items...'.format(item['name']))
        item_effects = transform_stats(item['effects'])
        rebuilt_item = {
            'dofusID': str(item['ankama_id']),
            'name': {
                'en': item['name'],
                'fr': item['name'],
                'de': item['name'],
                'es': item['name'],
                'it': item['name'],
                'pt': item['name']
            },
            'itemType': item['type']['name'],
            'setID': item['parent_set']['id'] if 'parent_set' in item else None,
            'level': item['level'],
            'stats': item_effects['stats'],
            'customStats': item_effects['customStats'],
            'conditions': transform_conditions(item['conditions']) if 'conditions' in item else {},
            'image': format_image_and_download(item['image_urls'])
        }
        categorize_item(rebuilt_item)
        print('Added {} to items'.format(item['name']))

    with open('output/items.json', 'w+', encoding='utf8') as outfile:
      outfile.write(json.dumps(final_items, ensure_ascii=False))
      outfile.close()

    with open('output/mounts.json', 'w+', encoding='utf8') as outfile:
      outfile.write(json.dumps(final_mounts, ensure_ascii=False))
      outfile.close()

    with open('output/pets.json', 'w+', encoding='utf8') as outfile:
      outfile.write(json.dumps(final_pets, ensure_ascii=False))
      outfile.close()

    with open('output/rhineetles.json', 'w+', encoding='utf8') as outfile:
      outfile.write(json.dumps(final_rhineetles, ensure_ascii=False))
      outfile.close()

    with open('output/weapons.json', 'w+', encoding='utf8') as outfile:
      outfile.write(json.dumps(final_weapons, ensure_ascii=False))
      outfile.close()


__main__ = transform_items()
