#!/usr/bin/env python3

# ./make_translation_json.py --sets diff/sets.diff --items diff/items.diff --pets diff/pets.diff --weapons diff/weapons.diff 

import json
import argparse


def process_diff(diff_lines):
    """
    Processes a diff file and pairs removed "en" key-value pairs
    with added ones into a dictionary.

    :param diff_lines: List of lines from the diff file
    :return: Dictionary pairing removed values with added values
    """
    pairs = {}

    for line in diff_lines:
        line = line.strip()

        # Check if it's a removed line with "en"
        if line.startswith('<') and '"en":' in line:
            # Extract the set name:
            key_name = line.split(': "')[-1].split('",')[0]

        # Check if it's an added line with "en"
        elif line.startswith('>') and '"en":' in line:
            if key_name:
                value_name = line.split(': "')[-1].split('",')[0]
                pairs[key_name] = value_name
                key_name = None  # Reset for the next pair

    return pairs


def main():
    parser = argparse.ArgumentParser(
        description="Read diffs and make a translation json for import.")
    parser.add_argument('--sets', type=str, help='Path to sets diff')
    parser.add_argument('--items', type=str, help='Path to items diff')
    parser.add_argument('--pets', type=str, help='Path to pets diff')
    parser.add_argument('--weapons', type=str, help='Path to weapons diff')

    args = parser.parse_args()

    try:
        # Open each file and read its content
        with open(args.sets, 'r') as sets_fd, open(args.items, 'r') as items_fd, open(args.pets, 'r') as pets_fd, open(args.weapons, 'r') as weapons_fd:
            sets_diff = sets_fd.readlines()
            items_diff = items_fd.readlines()
            pets_diff = pets_fd.readlines()
            weapons_diff = weapons_fd.readlines()

        out = {"sets": process_diff(sets_diff),
               "items": process_diff(items_diff),
               "pets": process_diff(pets_diff),
               "weapons": process_diff(weapons_diff),
               }

        print(json.dumps(out, indent=4))

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
