#!/bin/sh

# assumes you have a directory tree like:
# .
# ├── dofuslab
# └── dofuslab-items
cp -v output/*.json ../dofuslab/server/app/database/data/
