import csv
import os
import django
from django.db.models import Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FashionADs.settings")
django.setup()

from FashionStores.GetFilters import *
from FashionStores.models import *

# token = 'Bearer m7vH0nJpfv5KCcXB08VGEDDLrio6NggKa48yRlmmR9AFvmV7lqjSB5MR89Yl'
requestHeader = {'Content-Type': 'application/json'}
domainAndUrl = 'https://7b4a-39-50-19-253.ngrok.io/api/'


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


def PostStoresPromotion():
    stores = Store.objects.all()
    for store in stores:
        headerData, offerData = GettingData(store.Url)
        if offerData:
            if not OurStore.objects.filter(StoreName=store.Name, Nature='Store').exists():
                promos = GetStorePromo(headerData, offerData, store.Id)
                localStoreData = {"store_name": store.Name, "store_url": store.Url, "nature": "Store", "promos": promos}
                addingStoreUrl = domainAndUrl + 'saveCsvStore'
                PostToServer(addingStoreUrl, localStoreData)
                GetStoresDetail()
            else:
                promos = GetStorePromo(headerData, offerData, store.Id)
                localStoreData = {"store_name": store.Name, "store_url": store.Url, "nature": "Store", "promos": promos}
                saveStoreUrl = domainAndUrl + 'saveCsvStore'
                PostToServer(saveStoreUrl, localStoreData)


def GetStorePromo(headerData, offerData, storeId):
    promoDict = {}

    dealProduct = Product.objects.filter(StoreId=storeId).filter(Category__icontains='Deal')
    if dealProduct:
        promoDict['Deal'] = 'Yes'

    newProduct = Product.objects.filter(StoreId=storeId).filter(Category__icontains='New')
    if newProduct:
        promoDict['New Arrival'] = 'Yes'

    saleProduct = Product.objects.filter(StoreId=storeId).filter(Category__icontains='Sale')
    if saleProduct:
        promoDict['Sales'] = 'Yes'

    clearanceProduct = Product.objects.filter(StoreId=storeId).filter(Category__icontains='Clearance')
    if clearanceProduct:
        promoDict['Clearance'] = 'Yes'

    giftProduct = Product.objects.filter(StoreId=storeId).filter(
        (Q(Category__icontains='Gift') & (Q(Category__icontains='Card') | Q(Category__icontains='Voucher'))))
    if giftProduct:
        promoDict['Gift Cards'] = 'Yes'

    couponList = []
    couponCode = str(offerData[headerData.index('Coupon Code')]).title()
    if couponCode != '' and couponCode.lower() != 'no':
        for couponItem in list(couponCode.split(',')):
            couponList.append(
                'Get ' + couponItem.split('/')[0] + ' OFF Use Code: ' + couponItem.split('/')[1].split('(')[0])
        promoDict['Coupon Codes'] = ' PLUS => '.join(list(set(couponList)))

    shipCost = offerData[headerData.index('Shipping Cost')]
    if 'free' in shipCost.lower():
        promoDict['Free Shipping'] = 'Yes'

    priceMatch = str(offerData[headerData.index('Price match')]).title()
    if priceMatch != '' and priceMatch.lower() != 'no':
        promoDict['Price Match'] = 'Yes'

    priceGuarantee = str(offerData[headerData.index('Price Gurantee')]).title()
    if priceGuarantee != '' and priceGuarantee.lower() != 'no':
        promoDict['Price Guarantee'] = 'Yes'

    returnOffer = offerData[headerData.index('Return')]
    if 'free' in returnOffer.lower():
        promoDict['Free Return'] = 'Yes'

    exchange = offerData[headerData.index('Exchange')]
    if 'free' in exchange.lower():
        promoDict['Free Exchange'] = 'Yes'

    storePickUp = str(offerData[headerData.index('Store PickUp')]).title()
    if storePickUp != '' and storePickUp.lower() != 'no':
        promoDict['Store Pickup'] = 'Yes'

    return promoDict


def GettingData(storeUrl):
    csvPath = ''
    csvFile = ''
    try:
        csvPath = str((os.path.dirname(os.path.abspath(__file__)))).split('\FashionApp')[0]
        csvFile = open("FashionApp/Promotion.csv", "r")
    except:
        for root, dirs, files in os.walk(csvPath):
            for name in files:
                if name == "Promotion.csv":
                    csvFile = open(str(root) + "\\Promotion.csv", "r")

    csvreader = csv.reader(csvFile)
    headerData = next(csvreader)

    offerData = []
    for row in csvreader:
        if str(storeUrl).strip().rstrip('/') in row[headerData.index('Site Url')].strip().rstrip('/'):
            offerData = row
            break

    return headerData, offerData


def PostToServer(reqUrl, reqJson):
    try:
        reqJson = json.dumps(reqJson)
        print(reqJson)
        saveData = requests.post(url=reqUrl, data=reqJson, headers=requestHeader, timeout=6000)
        print(saveData.content)
    except Exception as e:
        print(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
        pass


# ========================== END =======================#
if __name__ == '__main__':
    PostStoresPromotion()