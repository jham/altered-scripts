# Script by Maverick CHARDET
# MIT License

# Parameters
ADD_TO_TRADELIST = False
ADD_TO_UNIQUESRANKING = True
CARDS_DATA_PATH = "results/cards.json"

# Imports
import json
import os
import requests
from os.path import exists
from utils import load_json

def main():
    if not os.path.exists(CARDS_DATA_PATH):
        print(f"File {CARDS_DATA_PATH} not found. Have you run get_cards_data.py?")
        return
    
    collection = load_json(CARDS_DATA_PATH)
    auth_token = None
    if exists("secret_token.txt"):
        with open ("secret_token.txt", "r") as f:
            auth_token = f.read()
    else:
        raise Exception("you must put your auth token in secret_token.txt")

    cards = []
    card_ids = []

    for card in collection.values():
        if not card["rarity"] == "UNIQUE":
            continue

        card_ids.append(card["id"])
        cards.append({
            "card": "/cards/" + card["id"],
            "quantity": 1,
        })

    if ADD_TO_TRADELIST:
        url = "https://api.altered.gg/ownership_lists/tradelist"
        headers = {"Authorization": auth_token}
        response = requests.put(url, headers = headers, json = {"cards": cards})
        if not response.ok:
            print(response)
            raise Exception("Request error. Is your token up to date?")

    if ADD_TO_UNIQUESRANKING:
        # NOTE: This doesn't work
        for card_id in ["ALT_COREKS_B_AX_05_U_4697"]:
            print(f"Adding uniquesranking for {card_id}")
            response = requests.post("https://uniquesranking.com/add_cards", headers=headers, data="card_string=" + card_id)
            print(response)
            if not response.ok:
                print(response)
                print(response.text)
                raise Exception("Request error. Is your token up to date?")            


if __name__ == "__main__":
    main()
