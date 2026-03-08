#!/bin/sh

python3 fetch.py items # fetch dofusdude items
python3 fetch.py sets  # fetch dofusdude sets
python3 fetch.py dofuslab # fetch current dofuslab data
python3 transform_sets.py --ignore_dofuslab # fully regenerate our sets
python3 transform_items.py --skip --download_imgs # download new images
python3 transform_items.py --import_dofuslab_titles --import_dofuslab_custom_conditions
# the above command regenerates items while preserving some custom data
#  that the dofusdude API doesn't have
