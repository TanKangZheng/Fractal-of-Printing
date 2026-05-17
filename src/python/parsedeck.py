# Third-Party Packages
import requests

# Helper Files
import slugify as slg
from main import TAB_NAMES

# Python Package
import os.path
import shutil
from urllib.parse import urlparse

class CardData:
    name = None
    imgLink = None

    def __repr__(self):
        return f"CardData(name='{self.name}', imgLink='{self.imgLink}')\n"

def parseDecklist(decklink:str, log_func=print):

    # If silvie.org, add json format as a param
    if ((source := urlparse(decklink).netloc) and ('silvie.org' in source)):
        response = requests.get(decklink, params={'format': 'json'})
    else:
        response = requests.get(decklink)
    print(f"Fetching data from {response.url}")
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