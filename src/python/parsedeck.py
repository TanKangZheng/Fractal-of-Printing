# Third-Party Packages
import requests
import scrython
from scrython.base import ScrythonRequestHandler

# Helper Files
import slugify as slg

# Python Package
import copy
import os.path
import shutil
import time

ScrythonRequestHandler.set_user_agent('MoxPrinter/0.1 (tankangzheng2000@gmail.com)')

class CardData:
    name = None
    set = None
    cn = None
    imgLink = None

    def __repr__(self):
        return f"CardData(name='{self.name}', set='{self.set}', cn='{self.cn}', imgLink='{self.imgLink}')\n"

def parseDecklist(decklist:str, log_func=print):
    splitList = decklist.split('\n')
    parsedList = []
    for entry in splitList:
        cardData = CardData()
        # Strip the card count
        entry = entry[entry.find(' ')+1:]
        # Strip the card foil identifier
        if entry.find('*F*') != -1:
            entry = entry[:entry.rfind('*F*')-1]
        # Save the card name
        cardData.name = entry[:entry.find('(')-1]
        # Save the card number
        cardData.cn = entry[entry.rfind(' ')+1:]
        # Save the set
        cardData.set = entry[entry.find('(')+1:entry.rfind(')')]
        parsedList.append(cardData)

    # Generate the list of card image links
    parsedList = generateCardImageLink(parsedList, log_func=log_func)

    return parsedList

def generateCardImageLink(cardList:list[CardData], log_func=print) -> list[CardData]:
    returnList = []
    for cardEntry in cardList:
        try:
            card = scrython.cards.ByCodeNumber(code=cardEntry.set, number=cardEntry.cn)
        except:
            log_func("Could not find card via set and number, attempting to use card name...")
            try:
                card = scrython.cards.Named(fuzzy=cardEntry.name)
            except:
                log_func(f"Could not find card via fuzzy search, skipping {cardEntry.name}...")
                continue
        log_func(f"Found {card.name}")

        # Check for double faced cards
        if card.image_uris == None:
            for face in card.card_faces:
                log_func(f"Processing {face.name}")
                faceCardEntry = CardData()
                faceCardEntry = copy.copy(cardEntry)
                faceCardEntry.name = face.name
                faceCardEntry.imgLink = face.image_uris['large']
                returnList.append(faceCardEntry)
        else:
            log_func(f"Processing {card.name}")
            cardEntry.imgLink = card.image_uris['large']
            returnList.append(cardEntry)

    return returnList
    
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

        # Scryfall mandated throttle
        time.sleep(0.1)

    except requests.RequestException as e:
        log_func(f"Error downloading {cardData.name}: {e}")