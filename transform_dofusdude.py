from os import path
import json
import requests
from constants import CUSTOM_STAT_MAP, NORMAL_STAT_MAP

dofusdude_data = open('input/dofusdude-example-2.json')
dofuslab_current_data = open('input/dofuslab-example-2.json')
serialized = json.load(dofusdude_data)
serialized_current = json.load(dofuslab_current_data)
final_items = []


def item_exists(id):
  for i in serialized_current:
    if i['dofusID'] == str(id):
      return True


def format_image_and_download(image_urls):
  dir_path = path.dirname(path.realpath(__file__))
  img_id = image_urls['icon'].split('item/')[1]
  subfolder = "output/images"
  complete_name = path.join(dir_path, subfolder, img_id)
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
      'customStats': custom_stats
  }


def transform_items():
  final_items = serialized_current
  for item in serialized:
    if item_exists(item['ankama_id']):
      print('{} is already in the list'.format(item['name']))
    else:
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
      final_items.append(rebuilt_item)
      print('Added {} to items'.format(item['name']))

    with open('output/dofuslab-data.json', 'w', encoding='utf8') as outfile:
      json.dump(final_items, outfile, indent=2, ensure_ascii=False)


__main__ = transform_items()
