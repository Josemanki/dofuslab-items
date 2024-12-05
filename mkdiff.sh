#!/bin/bash

set -x

mkdir -p diff

diff input/dofuslab/sets.json output/sets.json > diff/sets.diff
diff input/dofuslab/pets.json output/pets.json > diff/pets.diff
diff input/dofuslab/items.json output/items.json > diff/items.diff
diff input/dofuslab/weapons.json output/weapons.json > diff/weapons.diff
