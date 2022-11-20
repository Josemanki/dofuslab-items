import json

dofusdude_data = open('output/dofuslab-data.json')
serialized = json.load(dofusdude_data)
dofusdude_data.close()
item_types = []

for i in serialized:
  item_types.append(i['itemType'])

types_set = set(item_types)

print(types_set)
