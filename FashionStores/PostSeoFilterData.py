import os
import csv
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FashionADs.settings")
django.setup()
from FashionStores.GetFilters import *

# token = 'Bearer m7vH0nJpfv5KCcXB08VGEDDLrio6NggKa48yRlmmR9AFvmV7lqjSB5MR89Yl'
requestHeader = {'Content-Type': 'application/json'}
domainAndUrl = 'https://ec73-39-32-211-224.ngrok.io/api/'


def PostFilters():
    seoList = ['Description', 'Keyword']
    for seoType in seoList:
        categoryData = GettingData(seoType)
        while len(categoryData) != 0:
            PostToServer(domainAndUrl + 'save_seo_filter', categoryData[:100], seoType)
            del categoryData[0:100]


def GettingData(seoType):
    mainPath = str((os.path.dirname(os.path.abspath(__file__))))
    csvReader = csv.reader(open(os.path.join(mainPath, "Filter" + seoType + ".csv"), "r"))
    next(csvReader)
    return list(csvReader)


def PostToServer(reqUrl, reqJson, seoType):
    try:
        seoDict = {}
        seoDict[seoType.lower()] = reqJson
        reqJson = json.dumps(seoDict)
        saveData = requests.post(url=reqUrl, data=reqJson, headers=requestHeader, timeout=6000)
        print(saveData.content)
    except Exception as e:
        print(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
        pass


# ========================== END =======================#
if __name__ == '__main__':
    PostFilters()
