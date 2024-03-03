NORMAL_STAT_MAP = {
    "MP": "MP",
    "Vitality": "Vitality",
    "Wisdom": "Wisdom",
    "Heals": "Heals",
    "AP": "AP",
    "Intelligence": "Intelligence",
    "Fire Resistance": "Fire Resistance",
    "Earth Resistance": "Earth Resistance",
    "% Air Resistance": "% Air Resistance",
    "% Water Resistance": "% Water Resistance",
    "Chance": "Chance",
    "Initiative": "Initiative",
    "Prospecting": "Prospecting",
    "Lock": "Lock",
    "Water Damage": "Water Damage",
    "Summons": "Summons",
    "% Critical": "Critical",
    "Damage": "Damage",
    "Range": "Range",
    "Power": "Power",
    "Neutral Resistance": "Neutral Resistance",
    "% Neutral Resistance": "% Neutral Resistance",
    "Agility": "Agility",
    "% Fire Resistance": "% Fire Resistance",
    "Critical Damage": "Critical Damage",
    "MP Parry": "MP Parry",
    "% Melee Damage": "% Melee Damage",
    "% Weapon Damage": "% Weapon Damage",
    "Strength": "Strength",
    "Critical Resistance": "Critical Resistance",
    "Air Damage": "Air Damage",
    "Earth Damage": "Earth Damage",
    "Neutral Damage": "Neutral Damage",
    "MP Reduction": "MP Reduction",
    "Dodge": "Dodge",
    "Air Resistance": "Air Resistance",
    "Fire Damage": "Fire Damage",
    "Pushback Damage": "Pushback Damage",
    "% Earth Resistance": "% Earth Resistance",
    "AP Reduction": "AP Reduction",
    "% Melee Resistance": "% Melee Resistance",
    "Pushback Resistance": "Pushback Resistance",
    "% Ranged Damage": "% Ranged Damage",
    "AP Parry": "AP Parry",
    "Pods": "pods",
    "Water Resistance": "Water Resistance",
    "Power (traps)": "Power (traps)",
    "% Spell Damage": "% Spell Damage",
    "% Ranged Resistance": "% Ranged Resistance",
}

WEAPON_STAT_MAP = {
    "(Water damage)": "Water damage",
    "(Fire damage)": "Fire damage",
    "(Air damage)": "Air damage",
    "(Earth damage)": "Earth damage",
    "(Neutral damage)": "Neutral damage",
    "(Neutral steal)": "Neutral steal",
    "(Air steal)": "Air steal",
    "(Water steal)": "Water steal",
    "(Fire steal)": "Fire steal",
    "(Earth steal)": "Earth steal",
    "(HP restored)": "HP restored",
}

CUSTOM_STAT_MAP = [
    # "Exchangeable:",
    "Compatible with:",
    "% Critical Hit bonus on the spell",
    "Increases the spell's maximum range by",
    "no longer requires a line of sight",
    "Reduces the spell's cooldown period by",
    "Reduces the spell's AP cost by",
    "Increases the maximum number of times can be cast per turn by",
    "Effectiveness:",
    "Paddock Item",
    "Remaining uses:/",
    "HP",
    "Title:",
    "Teleport",
    "Different area to:",
    "Alignment level",
    "Restores energy points",
    "Set bonus",
    "Learn the spell level",
    "XP",
    "What's in there?",
    # "emote",
    "Be level or higher",
    "Positions the compass",
    "No future smithmagic",
    "% chance of success",
    "Cooperative crafting impossible",
    "Received on",
    "remaining fight(s)",
    "Get on/off a mount",
    "Summons a level",
    "Begins a quest",
    "Wrapped by:",
    "Linked to the character",
    "Have a mount equipped",
    " not equipped",
    "Change the attack element",
    "Hunting weapon",
    "Frees an enemy soul",
    "Learn the spell",
    "Subscribers only",
    "Level Incarnation",
    "Emote",
    "Teleport to save point",
    "is no longer linear",
    "Someone's following you!",
    "Last fed -",
    "Forget one level of the spell",
    "kama gain",
    "Damage on the spell:",
    "Frees enemy souls",
    "Revive the target",
    "Trap Damage",
    "Seeks",
    "Name:",
    "Ornament:",
    "Increases the maximum number of times can be cast per target by",
    "Changes appearance",
    "Makes the spell's range modifiable",
    "Changes speech",
    "Increases's basic damage by",
    "Heal",
    "% chance of capturing a mount",
    "Number of victims:",
    "Get a mount!",
    "Reflects damage",
    "level",
    "% chance of capturing a power soul",
    "Legendary Status",
    "Starts a fight against",
    "Applies a% experience bonus to professions for minutes",
    "Applies an experience bonus of% for minutes",
    "Reinitialise the effects of an item with a level equal to or less than",
    "Experience:",
    "Steals kamas",
    "Place a prism",
    "Teleport to the nearest allied prism",
    "Rename the alliance",
    "Prepares scrolls",
    "Write a character's name",
    "Switches alignment",
    "Globally Pre-Sentient",
    "Change the alliance's emblem",
    "Resuscitates allies on your map",
    "Change the guild's emblem",
    "Add a temporary spell",
    "Earth Resistance in PvP",
    "Neutral Resistance in PvP",
    "Water Resistance in PvP",
    "Fire Resistance in PvP",
    "Air Resistance in PvP",
    "% Air Resistance in PvP",
    "% Water Resistance in PvP",
    "% Fire Resistance in PvP",
    "% Neutral Resistance in PvP",
    "% Earth Resistance in PvP",
    "Remove an item from a Paddock",
    "Size: cells",
    "Use custom set n°",
    "Summons a Perceptor",
    "Rename the guild",
    "Rename guild:",
    "Get a divorce",
    "-special spell-",
    "The spell can be cast on a free cell",
]

PET_ITEM_TYPES = ["Pet", "Petsmount"]

DOFUSLAB_CATEGORIES = ["items", "mounts", "pets", "rhineetles", "sets", "weapons"]

WEAPON_TYPES = [
    "Axe",
    "Bow",
    "Dagger",
    "Lance",
    "Hammer",
    "Pickaxe",
    "Scythe",
    "Shovel",
    "Soul stone",
    "Staff",
    "Sword",
    "Tool",
    "Wand",
]

MOUNT_TYPES = [
    "Dragoturkey Certificate",

]

IGNORED_CATEGORIES = [
    "Sidekick",
    "Tool",
    "Pickaxe",
    "Soul stone",
    "Capturing net",
    "Magic weapon",
    "Expedition Idol",
]

IGNORED_ITEM_TYPES = [
    "Perceptor Daggers",
    "Perceptor Armour",
    "Perceptor Chests",
    "Perceptor Bags",
    "Perceptor Shoes",
    "Perceptor Tunic",
    "Perceptor Banner",
    # Temporis items:
    "Badge"
]

IGNORED_ITEM_IDS = [
    # Osatopia 2 pets:
    29115, # Naive Yakitoro
    29120, # Innocent Yakitoro
    29122, # Carefree Yakitoro
    29194, # Docile Yakitoro
    29216, # Ruminant Yakitoro
    29219, # Horned Yakitoro
    29221, # Slugger Yakitoro
    29223, # Hard-Charging Yakitoro
    29225, # Skewer-Happy Yakitoro

    # Temporis IDR which:
    27070, # Reincarnated Garudania
    27072, # Incubated Garudania
    27075, # Hatched Garudania
    27077, # Crackling Garudania

    # Eca city, the actual worst Temporis:
    25024, # Louz
    25032, # Catmeleon Louz

    # Quest Dofuses:
    21186, # Vulbis Dofus (quest version)
    27803, # Pine Done
    29134, # Sylvan Dofus (quest version)
    29135, # Verdant Dofus (quest item, basically Pine Done)

    # GM stuff:
    2154, # De Sendar's Ring, requires Player = Silaisie
    2155, # Jiva Necklace, requires Player = Silaisie
    2156, # Sword of Justice, requires Player = Silaisie
    6713, # Lordsoth Daggers, requires Player = Lordsoth
    8575, # First Blood Staff, requires Player = XxRamboPLxX
    6894, # Ultra-powerful Combat Bow Meow (GM)
    6895, # Small Combat Bow Meow (GM)
    7913, # Animagi (GM)
    9031, # Gore Master's Ring (Gms Only)
    9919, # Owl Ring, mentor ring
    

    # Title Shields:
    10158, # Trophy Dark Vlad Shield
    10159, # Trophy Moon Shield
    10160, # Trophy Soft Oak Shield
    10161, # Trophy Dragon Pig Shield
    10162, # Trophy Minotoror Shield
    10163, # Trophy Kimbo Shield
    10164, # Trophy Wa Wabbit Shield
    10165, # Trophy Koolich Shield
    10166, # Trophy Sphincter Cell Shield
    10167, # Trophy Bworker Shield

    # Random unabtainable/quest stuff:
    6800, # Basic Cloak
    677, # Pirate Cloak, unobtainable
    13063, # Split Splinter Sprinter, unequippable
    8854, # Crack Sparrow's Own Withered Hat, requires Server = Shika
    1628, # Fire Artefact, unobtainable
    1629, # Earth Artefact, unobtainable
    1630, # Air Artefact, unobtainable
    1631, # Water Artefact, unobtainable
    1632, # Light Artefact, unobtainable
    1633, # Life Artefact, unobtainable
    19641, # Nackle Tabard
    8627, # Sarr Ys's Flute, event reward, statless
    9627, # Apprentice Pilgrim Staff, statless, idk where from
    19639, # Syllabu Shield
    7097, # Training Shield
    15157, # Questhead, event hat, no stats
    2341, # Mech Riorraw's Bow, bonta quest bow
    2361, # Mulic Bere's Bow, brak quest bow
    8338, # Kwismas Sword, event/quest sword with no stats
    6773, # Tude Amulet, unobtainable from old Astrub quests
    21711, # Weighted Wooden Wings, quest item
    21712, # Weighted Helmet, quest item
    23094, # Panduckler, quest item
    27431, # Young Celestial Gobbly, seems unobtainable
    6839, # Yingnitiate Sword, Ecaflip + Male only
    6840, # Yanguru Sword, Ecaflip + Female only
    9396, # Zawooin's Seal, unobtainable item with no stats
    17627, # Experimental Foam Shield
    17628, # Experimental Wool Shield
    17629, # Experimental Trud Shield
    17684, # Improbability Magnifier
    17961, # Isolation Helmet
    23501, # Pandasiman Training Shield
    23563, # Voluntary Sacrifice
    23805, # Master Tor Toise's Training Shell
    29110, # Menologium
    29133, # Blessed Menologium
    26366, # Ochre Ring
    8701, # Nicked Sword, Ankama lottery
    10223, # Dontase Mebro shovel
    17460, # Bony Wand (quest item)
    17809, # Ereziah Hammer (quest item)
    19637, # Weapon Curse (quest item)
    25235, # Danaba's Blade (quest item)
]


SETS_BASE_URL = "https://api.dofusdu.de/dofus2/{}/sets/all"
ITEMS_BASE_URL = "https://api.dofusdu.de/dofus2/{}/items/equipment/all"
DOFUSLAB_GH_BASE_URL = "https://raw.githubusercontent.com/dofuslab/dofuslab/master/server/app/database/data/{}.json"