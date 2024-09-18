# Script by Maverick CHARDET
# MIT License

# Default config values. Put local changes in config.toml
DUMP_TEMP_FILES = False
OUTPUT_FOLDER = "results"
TEMP_FOLDER = "temp"
INCLUDE_PROMO_CARDS = False
INCLUDE_UNIQUES = False
INCLUDE_KS = True
FORCE_INCLUDE_KS_UNIQUES = False # only relevant if INCLUDE_KS = False and INCLUDE_UNIQUES = True
INCLUDE_FOILERS = False
SKIP_NOT_ALL_LANGUAGES = False
ONLY_LOAD_COLLECTION = True

# Imports
import json
import requests
import tomllib
from typing import Dict, List
from os.path import join, exists
from utils import dump_json, create_folder_if_not_exists, LANGUAGE_TO_LOCALE

# Constants
DEFAULT_ITEMS_PER_PAGE = 36
ALL_LANGUAGES = ["en", "fr", "es", "it", "de"]
ALL_FACTIONS = ["AX", "BR", "LY", "MU", "OR", "YZ", "NE"]

def get_page(apiEndpoint, language, page, faction=None, rarities=[], items_per_page=DEFAULT_ITEMS_PER_PAGE, collection_token=None, only_load_collection=True):
    url = f"https://api.altered.gg/{apiEndpoint}?itemsPerPage={items_per_page}&page={page}"
    for rarity in rarities:
        url += "&rarity[]=" + rarity
    headers = {}
    url += f"&locale={LANGUAGE_TO_LOCALE[language]}"
    if collection_token:
        headers.update({"Authorization": collection_token})
        if only_load_collection:
            url += f"&collection=true"
    if faction is not None:
        url += f"&factions[]={faction}"
    attempts = 0
    response = None
    while not response:
        attempts += 1
        if attempts > 1:
            print(f"Error ({url}). Retrying (attempt {attempts})...")
        try:
            response = requests.get(url, headers=headers)
        except:
            if attempts >= 5:
                raise
        if attempts >= 5:
            raise Exception("Didn't work after 5 attempts")
    if not response.ok:
        print(response)
        raise Exception("Request error." + (" Is your token up to date?" if collection_token else ""))
    data = response.json()
    cards = data["hydra:member"]
    if apiEndpoint == "cards":
        fix_api_errors(cards)
    return cards, int(data["hydra:totalItems"])


def fix_api_errors(cards):
    for card in cards:
        id: str = card["reference"]
        cn: str = card["collectorNumberFormatted"]
        if id.startswith("ALT_COREKS_B_LY_06_"): # Ouroboros Trickster KS
            card["collectorNumberFormatted"] = cn.replace("BTG-070", "BTG-065")
        if id.startswith("ALT_COREKS_B_LY_12_"): # Lyra Navigator KS
            card["collectorNumberFormatted"] = cn.replace("BTG-074", "BTG-070")
        if id.startswith("ALT_COREKS_B_LY_10_"): # Ouroboros Inkcaster KS
            card["collectorNumberFormatted"] = cn.replace("BTG-065", "BTG-074")

def get_data_language_faction(apiEndpoint, language, faction, rarities=[], items_per_page=DEFAULT_ITEMS_PER_PAGE, collection_token=None, only_load_collection=True):
    print("  page 1")
    data, page1_total = get_page(apiEndpoint, language, 1, faction=faction, rarities=rarities, items_per_page=items_per_page, collection_token=collection_token, only_load_collection=only_load_collection)
    if data is None:
        return None
    nb_pages = (page1_total - 1)//DEFAULT_ITEMS_PER_PAGE + 1
    for i in range(2, nb_pages+1):
        print(f"  page {i}/{nb_pages}")
        page_data, page_total = get_page(apiEndpoint, language, i, faction=faction, rarities=rarities, items_per_page=items_per_page, collection_token=collection_token, only_load_collection=only_load_collection)
        if page_total != page1_total:
            print("Restarting because the total number of cards changed")
            return get_data_language_faction(language, faction, collection_token=collection_token, only_load_collection=only_load_collection)
        data += page_data
    
    if len(data) != page1_total:
        raise Exception(f"Error: total ({page1_total}) is different compared to number of cards ({len(data)})")
    
    return data

def get_data_language(apiEndpoint, factions, language, rarities=[], items_per_page=DEFAULT_ITEMS_PER_PAGE, collection_token=None, only_load_collection=True):
    data = []
    if factions:
        for faction in factions:
            print(f"==== Faction {faction} ====")
            data += get_data_language_faction(apiEndpoint, language, faction, rarities=rarities, items_per_page=items_per_page, collection_token=collection_token,only_load_collection=only_load_collection)
        return data
    else:
        return get_data_language_faction(apiEndpoint, language, None, rarities=rarities, items_per_page=items_per_page, collection_token=collection_token,only_load_collection=only_load_collection)

def treat_cards_data(cards_data, stats_data, include_uniques, include_ks, include_promo_cards, include_foilers, force_include_ks_uniques):
    cards = []
    types = {}
    subtypes = {}
    factions = {}
    rarities = {}
    for card in cards_data:
        if not include_foilers and "_FOILER_" in card["reference"]:
            continue
        if not include_ks and "_COREKS_" in card["reference"]:
            if not include_uniques or not force_include_ks_uniques or "_U_" not in card["reference"]:
                continue
        if not include_promo_cards and card["reference"].startswith("ALT_CORE_P_"):
            # print(f"Skipping promo card {card['reference']}")
            continue # Promo card with missing stats
        cdata = {
            "id": card["reference"],
            "name": card["name"],
            "type": card["cardType"]["reference"],
            "subtypes": [subtype["reference"] for subtype in card["cardSubTypes"]] if "cardSubTypes" in card else [],
            "imagePath": card["imagePath"],
            "assets": card["assets"] if "assets" in card else [],
            "mainFaction": card["mainFaction"]["reference"],
            "elements": card["elements"],
            "rarity": card["rarity"]["reference"],
            "collectorNumberFormatted": card["collectorNumberFormatted"]
        }
        for stats in stats_data:
            if stats["reference"] == card["reference"]:
                for optional_property in ["inMyCollection", "inMyWantlist", "foiled", "inMyTradelist"]:
                    if optional_property in stats:
                        cdata[optional_property] = stats[optional_property]
        cards.append(cdata)

        types[card["cardType"]["reference"]] = card["cardType"]["name"]
        if "cardSubTypes" in card:
            for subtype in card["cardSubTypes"]:
                subtypes[subtype["reference"]] = subtype["name"]
        factions[card["mainFaction"]["reference"]] = card["mainFaction"]["name"]
        rarities[card["rarity"]["reference"]] = card["rarity"]["name"]
    return cards, types, subtypes, factions, rarities

def merge_language_dicts(data: Dict[str, Dict[str, any]]):
    merged_dict = {}
    for language in data:
        for key in data[language]:
            if key not in merged_dict:
                merged_dict[key] = {}
            merged_dict[key][language] = data[language][key]
    return merged_dict

def merge_cards_data(data: Dict[str, List[Dict[str, any]]], skip_not_all_languages, is_collection):
    cards_lang_dict = {}
    all_cards_ids = set()
    for language in data:
        cards_lang_dict[language] = {}
        for card in data[language]:
            cards_lang_dict[language][card["id"]] = card
            all_cards_ids.add(card["id"])
    
    all_cards = {}
    for card_id in all_cards_ids:
        card = {}
        for language in data:
            if card_id not in cards_lang_dict[language]:
                print(f"Card {card_id} not found in {language}")
                if skip_not_all_languages:
                    print("Skipping card")
                    break
                continue
            current_card_lang = cards_lang_dict[language][card_id]
            same_properties = ["id", "type", "subtypes", "assets", "mainFaction", "rarity"]
            if is_collection:
                same_properties.extend(["foiled", "inMyTradelist", "inMyCollection", "inMyWantlist"])
            for property in same_properties:
                if property not in current_card_lang:
                    print(f"Property {property} not in card {current_card_lang['name']}")
                    continue
                add_property_or_ensure_identical(card, property, current_card_lang[property])
            for property in ["name", "imagePath", "collectorNumberFormatted"]:
                if property not in card:
                    card[property] = {}
                card[property][language] = current_card_lang[property]
            collector_number_printed: str = current_card_lang["collectorNumberFormatted"]
            if collector_number_printed[-2:].isalpha():
                collector_number_printed = collector_number_printed[:-3]
            add_property_or_ensure_identical(card, "collectorNumberPrinted", collector_number_printed)
            if "elements" not in card:
                card["elements"] = {}
            for property in current_card_lang["elements"]:
                if "EFFECT" in property:
                    if property not in card["elements"]:
                        card["elements"][property] = {}
                    card["elements"][property][language] = current_card_lang["elements"][property]
                else:
                    value = current_card_lang["elements"][property]
                    if "COST" in property or "POWER" in property:
                        value = value if value != "" else None
                    if property in ["PERMANENT", "RESERVE"]:
                        value = int(value) if value != "" else None
                    add_property_or_ensure_identical(card["elements"], property, value)
        else: # Execute when the for loop is done, except if break
            all_cards[card_id] = card
    return all_cards

def add_property_or_ensure_identical(card, property_name, property_value):
    if property_name in card:
        if card[property_name] != property_value:
            print(f"Property {property_name} is different for card {card['id']}: {card[property_name]} != {property_value}")
    else:
        card[property_name] = property_value

def get_cards_data(
    languages=ALL_LANGUAGES,
    dump_temp_files=DUMP_TEMP_FILES,
    temp_folder=TEMP_FOLDER,
    skip_not_all_languages=SKIP_NOT_ALL_LANGUAGES,
    rarities=[],
    include_ks=INCLUDE_KS,
    include_promo_cards=INCLUDE_PROMO_CARDS,
    include_foilers=INCLUDE_FOILERS,
    force_include_ks_uniques=FORCE_INCLUDE_KS_UNIQUES,
    items_per_page=DEFAULT_ITEMS_PER_PAGE,
    factions=ALL_FACTIONS,
    collection_token=None,
    include_stats=False,
    only_load_collection=ONLY_LOAD_COLLECTION
):
    if dump_temp_files:
        create_folder_if_not_exists(temp_folder)

    treated_cards = {}
    treated_types = {}
    treated_subtypes = {}
    treated_factions = {}
    treated_rarities = {}

    include_uniques = False
    if not rarities or "UNIQUE" in rarities:
        include_uniques = True

    # Collection stats are not language specific, so only load them once, if there is a collection
    raw_stats_data = []
    if collection_token and include_stats:
        print("Importing stats data")
        raw_stats_data = get_data_language("cards/stats", factions, "en", rarities=rarities, items_per_page=items_per_page, collection_token=collection_token, only_load_collection=only_load_collection)
        if dump_temp_files:
            dump_json(raw_cards_data, join(temp_folder, 'raw_stats_data_' + language + '.json'))

    for language in languages:
        print("Importing card data for language " + language)
        raw_cards_data = get_data_language("cards", factions, language, rarities=rarities, items_per_page=items_per_page, collection_token=collection_token, only_load_collection=only_load_collection)
        if dump_temp_files:
            dump_json(raw_cards_data, join(temp_folder, 'raw_cards_data_' + language + '.json'))
        tcards, ttypes, tsubtypes, tfactions, trarities = treat_cards_data(
            raw_cards_data,
            raw_stats_data,
            include_uniques=include_uniques,
            include_ks=include_ks,
            include_promo_cards=include_promo_cards,
            include_foilers=include_foilers,
            force_include_ks_uniques=force_include_ks_uniques
        )
        if DUMP_TEMP_FILES:
            dump_json(tcards   , join(temp_folder, 'cards_' + language + '.json'))
            dump_json(ttypes   , join(temp_folder, 'types_' + language + '.json'))
            dump_json(tsubtypes, join(temp_folder, 'subtypes_' + language + '.json'))
            dump_json(tfactions, join(temp_folder, 'factions_' + language + '.json'))
            dump_json(trarities, join(temp_folder, 'rarities_' + language + '.json'))
        treated_cards[language] = tcards
        treated_types[language] = ttypes
        treated_subtypes[language] = tsubtypes
        treated_factions[language] = tfactions
        treated_rarities[language] = trarities

    cards    = merge_cards_data(treated_cards, skip_not_all_languages=skip_not_all_languages, is_collection=include_stats)
    types    = merge_language_dicts(treated_types)
    subtypes = merge_language_dicts(treated_subtypes)
    factions = merge_language_dicts(treated_factions)
    rarities = merge_language_dicts(treated_rarities)
    return cards, types, subtypes, factions, rarities

if __name__ == "__main__":
    config = {}
    if exists("config.toml"):
        with open("config.toml", "rb") as f:
            config = tomllib.load(f)

    collection_token = None
    if exists("secret_token.txt"):
        with open ("secret_token.txt", "r") as f:
            collection_token = f.read()

    cards, types, subtypes, factions, rarities = get_cards_data(
        languages = config.get("languages", ALL_LANGUAGES),
        dump_temp_files = config.get("dump_temp_files", DUMP_TEMP_FILES),
        temp_folder = config.get("temp_folder", TEMP_FOLDER),
        skip_not_all_languages = config.get("skip_not_all_languages", SKIP_NOT_ALL_LANGUAGES),
        include_uniques = config.get("include_uniques", INCLUDE_UNIQUES),
        include_ks = config.get("include_kickstarter", INCLUDE_KS),
        include_promo_cards = config.get("include_promo_cards", INCLUDE_PROMO_CARDS),
        include_foilers = config.get("include_foilers", INCLUDE_FOILERS),
        force_include_ks_uniques = config.get("force_include_ks_uniques", FORCE_INCLUDE_KS_UNIQUES),
        items_per_page = config.get("items_per_page", DEFAULT_ITEMS_PER_PAGE),
        factions = config.get("factions", ALL_FACTIONS),
        collection_token = collection_token,
        include_stats = collection_token is not None,
        only_load_collection = config.get("only_load_collection", ONLY_LOAD_COLLECTION),
    )
    create_folder_if_not_exists(OUTPUT_FOLDER)
    dump_json(cards,    join(OUTPUT_FOLDER, 'cards.json'))
    dump_json(types,    join(OUTPUT_FOLDER, 'types.json'))
    dump_json(subtypes, join(OUTPUT_FOLDER, 'subtypes.json'))
    dump_json(factions, join(OUTPUT_FOLDER, 'factions.json'))
    dump_json(rarities, join(OUTPUT_FOLDER, 'rarities.json'))

