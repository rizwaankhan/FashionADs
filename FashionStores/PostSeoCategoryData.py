import os
import csv
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FashionADs.settings")
django.setup()
from FashionStores.GetFilters import *

# token = 'Bearer m7vH0nJpfv5KCcXB08VGEDDLrio6NggKa48yRlmmR9AFvmV7lqjSB5MR89Yl'
requestHeader = {'Content-Type': 'application/json'}
domainAndUrl = 'https://ab22-39-32-211-224.ngrok.io/api/'


# ================ GET AUTH TOKEN  =====================#
# def GetAuthorizationToken():
#     print('GETTING NEW AUTH TOKEN ....!')
#
#     loginUrl = domainAndUrl + 'login'
#     apiResponse = requests.post(url=loginUrl, data='{"email":"apiuser@gmail.com","password":"kasAU2ASLDa82"}',
#                                 headers=requestHeader, timeout=6000)
#     apiJson = json.loads(apiResponse.content)
#     authToken = 'Bearer ' + apiJson['token']
#     return authToken


def PostCategories():
    seoList = ['Description', 'Keyword']
    for seoType in seoList:
        categoryData = GettingData(seoType)
        while len(categoryData) != 0:
            PostToServer(domainAndUrl + 'save_seo_category', categoryData[:100], seoType)
            del categoryData[0:100]


def GettingData(seoType):
    mainPath = str((os.path.dirname(os.path.abspath(__file__))))
    csvReader = csv.reader(open(os.path.join(mainPath, "Category" + seoType + ".csv"), "r"))
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
    PostCategories()
