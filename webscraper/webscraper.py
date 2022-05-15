import requests
from bs4 import BeautifulSoup
import time
from colorama import Fore, Back, Style
import json

plants = '[\n'
fieldNames = set()

def processData(key, value, plantDict:dict):
    if key == 'Name:':
        plantDict['name'] = value
    elif key == 'Latin_Name:':
        plantDict['latin_name'] = value
    elif key == 'URL:':
        plantDict['url'] = value
    elif key == 'Family:':
        plantDict['family'] = [e.strip() for e in value.split(',')]
    elif key == 'Group:':
        plantDict['group'] = value
    elif key == 'Flowers:':
        plantDict['flowers'] = value
    elif key == 'Leaves:':
        plantDict['leaves'] = [e.strip() for e in value.split(',')]
    elif key == 'Height:':
        plantDict['height'] = value
    elif key == 'Habitat:':
        plantDict['habitat'] = [e.strip() for e in value.split(',')]
    elif key == 'Grows in Sun/Shade:':
        plantDict['grows_in_sun_or_shade'] = [e.strip() for e in value.split(',')]
    elif key == 'Native/Non-native:':
        plantDict['native'] = True if value == 'Native' else False
    else:
        fieldNames.add(key)



def getNestedData(topElement, plantDict):
    children = topElement.findChildren('span', recursive=False)

    if len(children) < 1:
        return

    nextSpanElementName = children[0].text.strip()
    nextSpanElementData = children[1].text.strip()

    if nextSpanElementName == 'Flowers:':
        seasons = []
        colors = []
        petals_count = 0
        petals_shape = ''

        data = children[1].findChildren('a')
        for i in data:
            link = i.get('href')

            if link.startswith('http://ontariowildflowers.com/main/season.php'):
                seasons.append(i.text.strip())
            elif link.startswith('http://ontariowildflowers.com/main/colour.php'):
                colors.append(i.text.strip())
            elif link.startswith('http://ontariowildflowers.com/main/petals.php'):
                splitString = [e.strip() for e in i.text.split(' ')]
                if splitString[0].isdigit():
                    petals_count = int(splitString[0])
                else:
                    petals_shape = splitString[0]
            else:
                print(Fore.RED, link)

        
        nextSpanElementData = {
            'season':seasons,
            'color':colors,
            'petals_count':petals_count,
            'shape':petals_shape
        }


    processData(nextSpanElementName, nextSpanElementData, plantDict)

    print(Fore.GREEN + nextSpanElementName + Fore.WHITE + str(nextSpanElementData))

    for c in children[2:]:
        getNestedData(c, plantDict)



def getAllData(plant, plantDict):
    plantNames = plant.find('h1').getText().split('\n')

    plantNameEng = plantNames[0].strip()
    plantNameLat = plantNames[1].strip()

    processData('Name:', plantNameEng, plantDict)
    processData('Latin_Name:', plantNameLat, plantDict)

    print(Fore.GREEN + 'Name:' + Fore.WHITE + plantNameEng)
    print(Fore.GREEN + 'Latin_Name:' + Fore.WHITE + str(plantNameLat))

    plantData = plant.find('span', class_='Species_ItemData')

    getNestedData(plantData, plantDict)



def getPlantData(link):
    global plants
    plantDict = {}
    r = requests.get(link)

    print(Fore.CYAN + r.url)

    processData('URL:', r.url, plantDict)

    soup = BeautifulSoup(r.content, 'html.parser')

    plant = soup.find('table', class_='MainBody')
    if plant is not None:
        getAllData(plant, plantDict)
        plants += json.dumps(plantDict) + ', \n'
        print(plantDict)
        return 200
    else:
        print(Fore.RED + str(r))
        return 403



def main():
    global plants
    r = requests.get('http://ontariowildflowers.com/main/list_common.php')

    print(Fore.CYAN + r.url)

    soup = BeautifulSoup(r.content, 'html.parser')

    s = soup.find('table', class_='MainBody')
    content = s.find_all('li')
    i = 1
    for line in content:
        print(Fore.YELLOW + 'Processing record #' + str(i))
        link = line.find('a')
        while True:
            if (getPlantData(link.get('href')) == 200):
                break

            time.sleep(10)
        i+=1
        if i > 10_000:
            break

    print(Fore.RED, sorted(list(fieldNames)))
    #print(Fore.GREEN, plants)

    plants = plants[0:-3]
    plants += '\n]'

    with open('Database.json', 'w') as f:
        f.write(plants)



if __name__ == '__main__':
    main()