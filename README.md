# DofusLab Items

This repository is to facilitate updating DofusLab's data from [Survival's tools](https://docs.dofusdu.de/), particularly [doduda](https://github.com/dofusdude/doduda) for extracting client data, and then using scripts here to transform them to DofusLab's format.

## Running

Run the appropriate `transform_*.py` script.

You can find your output in the the `output` directory.

## Caveats

The transformation of item stats works mostly perfectly, but as this is still mostly a WIP tool to be used sparingly, there is stuff to be checked manually. A clear example of this would be that the tool has not yet blacklisted items that we purposely do not add to Dofuslab (eg. perceptor items), meaning that we can fully confidently copy-paste the items and sets individually, but the tool does not yet allow to replace the whole file.

## Dofus Update Notes

Typically, to update our data, you'll want to run something like:

```bash
python3 fetch.py items
python3 fetch.py sets
python3 fetch.py dofuslab
python3 transform_sets.py -i
python3 transform_items.py -s -d # skips existing, downloads new images
python3 transform_items.py -t -c # imports our dofuslab titles & custom conditions, generates all items
```
