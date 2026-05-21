# Third-Party Packages
import requests

# Helper Files
import slugify as slg
from main import TAB_NAMES

# Python Package
import os.path
import shutil
from urllib.parse import urlparse
import re

SILVIE_GG_SECTION_MAP = {
    "main deck:":       TAB_NAMES[0],
    "material deck":    TAB_NAMES[1],
    "sideboard":        TAB_NAMES[2]
}

class CardData:
    name = None
    imgLink = None

    def __init__(self, name: str = "", imgLink: str = ""): 
        self.name = name
        self.imgLink = imgLink

    def __repr__(self):
        return f"CardData(name='{self.name}', imgLink='{self.imgLink}')\n"

def parseDecklist_SilvieGG(decklink: str, log_func=print):
    # Convert Silvie.gg url to api endpoint
    decklink = decklink.replace("silvie.gg/", "silvie.gg/api/", 1)
    response = requests.get(decklink)
    log_func(f"Fetching data from {response.url}")
    if response.status_code == 200:
        deckinfo = response.json()
    else:
        log_func("Error fetching response!")
        return None

    decklist   = deckinfo["decklist"]
    cardImages = deckinfo["cardImages"]

    # Split the json data into sections
    sectionPattern = re.compile(r'^(Material deck|Main deck|Sideboard):$', re.MULTILINE | re.IGNORECASE)
    sections = {tab: [] for tab in TAB_NAMES}
    currentKey = None

    for decklistEntry in decklist.splitlines():
        header = sectionPattern.match(decklistEntry)
        if header:
            currentKey = SILVIE_GG_SECTION_MAP.get(header.group(1).lower())  # normalise to lowercase for map lookup
        elif decklistEntry and currentKey:
            sections[currentKey].append(decklistEntry.strip())

    # Create dicts: each tab → list of CardData
    def build_dict(card_lines, tab_name):
        result = []
        for line in card_lines:
            match = re.match(r'^\d+\s+(.+)$', line)
            if match:
                name    = match.group(1)
                imgLink = cardImages.get(name)
                result.append(CardData(name=name, imgLink=imgLink))
                log_func(f"[{tab_name}]: Added {name} with link: {imgLink}")
        return result

    parsedList = {tab: build_dict(sections[tab], tab) for tab in TAB_NAMES}
    return parsedList

def parseDecklist_SilvieOrg(decklink: str, log_func=print):
    response = requests.get(decklink, params={'format': 'json'})
    log_func(f"Fetching data from {response.url}")
    if (response.status_code == 200):
        deckinfo = response.json()
    else:
        log_func("Error fetching response!")
        return None
    
    parsedList = {}
    for deckType in TAB_NAMES:
        subdeckList = []
        cardEntries = deckinfo.get('cards', {}).get(deckType.lower(), [])
        for entry in cardEntries:
            cardData = CardData()
            cardData.imgLink = entry.get("image")
            cardData.name = entry.get("name")
            log_func(f"Added {cardData.name} with link: {cardData.imgLink}")
            subdeckList.append(cardData)
            if (entry.get("orientation") is not None):
                altCardData = CardData()
                altCardEntry = entry.get("orientations")[0]
                altCardData.imgLink = altCardEntry.get("image")
                altCardData.name = altCardEntry.get("name")
                log_func(f"Added {altCardData.name} with link: {altCardData.imgLink}")
                subdeckList.append(altCardData)
        parsedList[deckType] = subdeckList

    return parsedList

def parseDecklist(decklink:str, log_func=print):
    domain = urlparse(decklink).netloc

    if (domain == "silvie.gg"):
        return parseDecklist_SilvieGG(decklink, log_func)
    elif (domain == "silvie.org"):
        return parseDecklist_SilvieOrg(decklink, log_func)
    else:
        return None

def saveImage(cardData:CardData, savepath, log_func=print):
    image_name = slg.slugify(cardData.name) + ".png"
    path = os.path.join(savepath, image_name)
    log_func(f"Downloading {cardData.imgLink}")
    try:
        with requests.get(
            cardData.imgLink,
            stream=True,
            timeout=15
        ) as r:
            if r.status_code != 200:
                log_func(f"Failed ({r.status_code}): {cardData.name}")
                return
            with open(path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

    except requests.RequestException as e:
        log_func(f"Error downloading {cardData.name}: {e}")