# Third-Party Packages
import requests

# Helper Files
import slugify as slg

# Python Package
import os.path
import shutil

class CardData:
    name = None
    imgLink = None

    def __repr__(self):
        return f"CardData(name='{self.name}', imgLink='{self.imgLink}')\n"

def parseDecklist(decklink:str, log_func=print):

    response = requests.get(decklink, params={'format': 'json'})
    print(f"Fetching data from {response.url}")
    if (response.status_code == 200):
        deckinfo = response.json()
    else:
        log_func("Error fetching response!")
        return None

    mainCards = deckinfo.get('cards', {}).get('main', [])

    parsedList = []
    for entry in mainCards:
        cardData = CardData()
        cardData.imgLink = entry.get("image")
        cardData.name = entry.get("name")
        log_func(f"Added {cardData.name} with link: {cardData.imgLink}")
        parsedList.append(cardData)

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