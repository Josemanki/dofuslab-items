from os import path
import json
import requests

dofusdude_data = open('input/dofusdude-example.json')
serialized = json.load(dofusdude_data)
final_items = []

def format_image_and_download(image_urls):
  dir_path = path.dirname(path.realpath(__file__))
  img_id = image_urls['icon'].split('item/')[1]
  subfolder = "output/images"
  complete_name = path.join(dir_path, subfolder, img_id)
  img_data = requests.get(image_urls['icon']).content
  print(complete_name)
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
  final_stats = []
  for stat in stats:
    final_stats.append({
      'stat': stat['type']['name'],
      'minStat': stat['int_minimum'] if stat['int_maximum'] != 0 else None,
      'maxStat': stat['int_maximum'] if stat['int_maximum'] != 0 else stat['int_minimum']
    })
  return final_stats

def transform_items():

  for item in serialized:
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
      'stats': transform_stats(item['effects']),
      'customStats': {},
      'conditions': transform_conditions(item['conditions']) if 'conditions' in item else {},
      'image': format_image_and_download(item['image_urls'])
    }
    final_items.append(rebuilt_item)

  print(json.dumps(final_items))
  with open('output/dofuslab-data.json', 'w') as outfile:
    json.dump(final_items, outfile, indent=2)

__main__ = transform_items()