import json

dofusdude_data = open('output/dofuslab-data.json')
serialized = json.load(dofusdude_data)
dofusdude_data.close()
item_types = []
