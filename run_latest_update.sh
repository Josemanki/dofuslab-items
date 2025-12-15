#!/bin/sh

python3 fetch.py items
python3 fetch.py sets
python3 fetch.py dofuslab
python3 transform_sets.py -i
python3 transform_items.py -s -d
python3 transform_items.py -t -c
