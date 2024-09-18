# Script by Maverick CHARDET
# CC-BY

LANGUAGE_TO_LOCALE = {
    "en": "en-us",
    "fr": "fr-fr",
    "es": "es-es",
    "it": "it-it",
    "de": "de-de",
}

# Imports
import requests
import os
import json

def create_folder_if_not_exists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def download_file(url, filename, log=False, headers=None):
    if log: print(f"Downloading {filename} from {url}")
    response = requests.get(url, stream=True, headers=headers)
    if not response.ok:
        print(response)
        return False
    with open(filename, 'wb') as handle:
        for block in response.iter_content(1024):
            if not block:
                break
            handle.write(block)
    return True

def dump_json(data, filename):
    with open(filename, 'w', encoding="utf8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json(filename):
    with open(filename, encoding="utf8") as f:
        return json.load(f)

def load_txt(filename):
    with open(filename, encoding="utf8") as f:
        return f.read()
