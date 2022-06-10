import json
import os
import traceback

import django
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FashionADs.settings")
django.setup()
from FashionStores.models import *

# domainAndUrl = 'http://38.17.54.111:500/api/'


domainAndUrl = 'https://django.adscombined.com/api/'


# requestBody = '{"email":"apiuser@gmail.com","password":"kasAU2ASLDa82"}'
# token = 'Bearer m7vH0nJpfv5KCcXB08VGEDDLrio6NggKa48yRlmmR9AFvmV7lqjSB5MR89Yl'
# reqHeader = {'accept': 'application/json', 'content-type': 'application/json; charset=utf-8', 'Authorization': token}


# def GetAuthorizationToken():
#     print('GETTING NEW AUTH TOKEN ....!')
#
#     loginUrl = domainAndUrl + 'login'
#     apiResponse = requests.post(url=loginUrl, data=requestBody, headers=reqHeader, timeout=6000)
#     apiJson = json.loads(apiResponse.content)
#     authToken = 'Bearer ' + apiJson['token']
#     return authToken


def AllFilters():
    try:
        filtersData = requests.get(url=domainAndUrl + 'fetch_all_filters', timeout=6000,verify=False)
        filtersJson = json.loads(filtersData.text)
        filterTypes = list(filtersJson['data'].keys())
        filterTypes.remove('size')
        GetFilters(filtersJson, filterTypes)
        categoryData = requests.get(url=domainAndUrl + 'fetch_all_categories', timeout=6000, verify=False)
        categoryJson = json.loads(categoryData.text)
        GetCategory(categoryJson)
    except Exception as e:
        print(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))


def GetFilters(filtersJson, filterTypes):
    for filterType in filterTypes:
        if 'color' in filterType:
            GetColor(filtersJson, filterType)
        else:
            filterList = []
            for filterToken in filtersJson['data'][filterType]:
                parentID = filterToken['parent_category_id']
                filterID = filterToken['id']
                parentName = filterToken['parent_category_name']
                filterName = filterToken['filter_name']
                filterKeywords = filterToken['keywords']
                item = str(parentName), str(parentID), str(filterName), str(filterID), str(filterKeywords)
                filterList.append(item)
            SaveToPY(str(filterType).title().replace('_', '') + " = ", str(filterList))

    filterList = ['free_returns', 'returns_accepted', 'benefits_charity', 'authenticity_guarantee',
                  'climate_pledge_friendly']
    SaveToPY("ShowOnly = ", str(filterList))


def GetColor(filtersJson, filterType):
    for filterToken in filtersJson['data'][filterType]:
        colorID = filterToken['id']
        colorName = filterToken['filter_name']
        OurColor.objects.update_or_create(ColorID=colorID, ColorName=colorName)


def GetCategory(categoryJson):
    filterList = []
    for categoryToken in categoryJson['data']:
        parentID = categoryToken['parent_category_id']
        categoryID = categoryToken['id']
        parentName = categoryToken['parent_category_name']
        categoryName = categoryToken['category_name']
        categoryKeywords = categoryToken['keywords']
        item = str(parentName), str(parentID), str(categoryName), str(categoryID), str(categoryKeywords)
        filterList.append(item)
    SaveToPY(str('Category').title().replace('_', '') + " = ", str(filterList))


def SaveToPY(listName, listDetail):
    with open('allfilters.py', 'a', encoding='UTF8', newline='') as f:
        f.seek(0)
        data = f.read(100)
        if len(data) > 0:
            f.write("\n")
        f.write(listName + str(listDetail))


def GetStoresDetail():
    storeToken = requests.get(url=domainAndUrl + 'fetch_all_stores', timeout=6000 ,verify=False)
    storeJson = json.loads(storeToken.text)
    for storeToken in storeJson['data']:
        storeID = storeToken['id']
        nature = storeToken['nature']
        storeUrl = str(storeToken['store_url']).rstrip('/')
        storeName = storeToken['store_name']
        if OurStore.objects.filter(StoreID=storeID, StoreName=storeName, Nature=nature).exists():
            existingStore = OurStore.objects.get(StoreID=storeID, StoreName=storeName, Nature=nature).StoreUrl
            if existingStore == '' or existingStore is None:
                OurStore.objects.filter(StoreID=storeID, StoreName=storeName, Nature=nature).update(
                    StoreID=storeID, StoreName=storeName, StoreUrl=storeUrl, Nature=nature)
            else:
                pass
        else:
            OurStore(StoreID=storeID, StoreName=storeName, StoreUrl=storeUrl, Nature=nature).save()


if __name__ == '__main__':
    print('Getting Data from API')
    # AllFilters()
    GetStoresDetail()
    print('Saved Data')
