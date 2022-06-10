import datetime
import json
import re
import sys, os, operator
import traceback

import unidecode as unidecode
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import *
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from functools import reduce
from django.db import connection
from py_linq import Enumerable
from FashionStores.models import *


@api_view(['POST'])
@csrf_exempt
def save_db_records(request):
    try:
        reqJson = json.loads(json.dumps(request.data))
    except Exception as e:
        ex = ShowException(e)
        context = {'Error': 'Error getting database data: ' + str(ex), 'return_data': []}
        return Response(context)

    if reqJson.get('lockedData') is not None:
        SaveLockedData(reqJson.get('lockedData'))
    elif reqJson.get('product') is not None:
        SaveProducts(reqJson.get('product'))
    elif reqJson.get('productFilterIDs') is not None:
        SaveProFilterIDs(reqJson.get('productFilterIDs'))
    elif reqJson.get('productFilters') is not None:
        SaveProFilters(reqJson.get('productFilters'))
    elif reqJson.get('productSize') is not None:
        SaveProSizes(reqJson.get('productSize'))
    elif reqJson.get('scrapError') is not None:
        SaveScrapErrors(reqJson.get('scrapError'))
    elif reqJson.get('scrapResult') is not None:
        SaveScrapResults(reqJson.get('scrapResult'))
    elif reqJson.get('scraptype') is not None:
        SaveScrapTypes(reqJson.get('scraptype'))
    elif reqJson.get('store') is not None:
        SaveStores(reqJson.get('store'))


def SaveLockedData(lockedData):
    for lockedDict in lockedData:
        LockedData(Id=lockedDict['Id'], ProductId=lockedDict['ProductId'],
                   ScraperResultID=lockedDict['ScraperResultID'], StoreName=lockedDict['StoreName'],
                   ProductUrl=lockedDict['ProductUrl'], Color=lockedDict['Color'], Size=lockedDict['Size'],
                   DressStyle=lockedDict['DressStyle'], Occasion=lockedDict['Occasion'],
                   Material=lockedDict['Material'], MaterialPercentage=lockedDict['MaterialPercentage'],
                   DateCreated=lockedDict['DateCreated'], DateUpdated=lockedDict['DateUpdated'],
                   MachineNo=lockedDict['MachineNo']).save()


def SaveProducts(products):
    for proDict in products:
        Product(Id=proDict['Id'], StoreId=proDict['StoreId'], Url=proDict['Url'], Name=proDict['Name'],
                Price=proDict['Price'], SalePrice=proDict['SalePrice'], Brand=proDict['Brand'],
                ImageUrl=proDict['ImageUrl'], Category=proDict['Category'], Description=proDict['Description'],
                UPC_SKU=proDict['UPC_SKU'], Deleted=proDict['Deleted'],
                UpdatedOrAddedOnLastRun=proDict['UpdatedOrAddedOnLastRun'], DateCreated=proDict['DateCreated'],
                DateUpdated=proDict['DateUpdated'], MachineNo=proDict['MachineNo']).save()


def SaveProFilterIDs(proFilterIDs):
    for idDict in proFilterIDs:
        ProductFilterIDs(Id=idDict['Id'], ProductUrl=idDict['ProductUrl'], Character=idDict['Character'],
                         Closure=idDict['Closure'], DressLength=idDict['DressLength'], DressStyle=idDict['DressStyle'],
                         Embellishment=idDict['Embellishment'], Feature=idDict['Feature'], FitType=idDict['FitType'],
                         GarmentCare=idDict['GarmentCare'], Material=idDict['Material'],
                         MaterialPercentage=idDict['MaterialPercentage'], Neckline=idDict['Neckline'],
                         Occasion=idDict['Occasion'], Pattern=idDict['Pattern'], FasteningType=idDict['FasteningType'],
                         CuffStyle=idDict['CuffStyle'], Collar=idDict['Collar'], SleveesLength=idDict['SleveesLength'],
                         SleveesType=idDict['SleveesType'], Themes=idDict['Themes'], Season=idDict['Season'],
                         ShowOnly=idDict['ShowOnly'], ParentCategory=idDict['ParentCategory'],
                         Category=idDict['Category'], DateCreated=idDict['DateCreated'],
                         DateUpdated=idDict['DateUpdated'], MachineNo=idDict['MachineNo']).save()


def SaveProFilters(proFilters):
    for filtterDict in proFilters:
        ProductFilters(Id=filtterDict['Id'], ProductUrl=filtterDict['ProductUrl'], Character=filtterDict['Character'],
                       Closure=filtterDict['Closure'], DressLength=filtterDict['DressLength'],
                       DressStyle=filtterDict['DressStyle'], Embellishment=filtterDict['Embellishment'],
                       Feature=filtterDict['Feature'], FitType=filtterDict['FitType'],
                       GarmentCare=filtterDict['GarmentCare'], Material=filtterDict['Material'],
                       MaterialPercentage=filtterDict['MaterialPercentage'], Neckline=filtterDict['Neckline'],
                       Occasion=filtterDict['Occasion'], Pattern=filtterDict['Pattern'],
                       FasteningType=filtterDict['FasteningType'], CuffStyle=filtterDict['CuffStyle'],
                       Collar=filtterDict['Collar'], SleveesLength=filtterDict['SleveesLength'],
                       SleveesType=filtterDict['SleveesType'], Themes=filtterDict['Themes'],
                       Season=filtterDict['Season'], ShowOnly=filtterDict['ShowOnly'],
                       ParentCategory=filtterDict['ParentCategory'], Category=filtterDict['Category'],
                       DateCreated=filtterDict['DateCreated'], DateUpdated=filtterDict['DateUpdated'],
                       MachineNo=filtterDict['MachineNo']).save()


def SaveProSizes(proSizes):
    for sizeDict in proSizes:
        ProductSize(Id=sizeDict['Id'], ProductId=sizeDict['ProductId'], Color=sizeDict['Color'],
                    FitType=sizeDict['FitType'], Size=sizeDict['Size'], MappedSize=sizeDict['MappedSize'],
                    Available=sizeDict['Available'], Price=sizeDict['Price'], SalePrice=sizeDict['SalePrice'],
                    DateCreated=sizeDict['DateCreated'], DateUpdated=sizeDict['DateUpdated'],
                    MachineNo=sizeDict['MachineNo']).save()


def SaveScrapErrors(scrapErrors):
    for errorDict in scrapErrors:
        ScrapError(Id=errorDict['Id'], ScrapResultId=errorDict['ScrapResultId'], Message=errorDict['Message'],
                   StackTrace=errorDict['StackTrace'], UrlList=errorDict['UrlList'], Count=errorDict['Count'],
                   Exception=errorDict['Exception'], DateCreated=errorDict['DateCreated'],
                   MachineNo=errorDict['MachineNo']).save()


def SaveScrapResults(scrapResults):
    for resultDict in scrapResults:
        ScrapResult(Id=resultDict['Id'], StoreId=resultDict['StoreId'],
                    ScrapTypeId=resultDict['ScrapTypeId'], StartDateTime=resultDict['StartDateTime'],
                    EndDateTime=resultDict['EndDateTime'], NewProductUrlCount=resultDict['NewProductUrlCount'],
                    ExistingProductUrlCount=resultDict['ExistingProductUrlCount'],
                    TotalDistinctProductUrlCount=resultDict['TotalDistinctProductUrlCount'],
                    ProductAddedCount=resultDict['ProductAddedCount'],
                    ProductUpdatedCount=resultDict['ProductUpdatedCount'],
                    ProductDeletedCount=resultDict['ProductDeletedCount'],
                    ProductMergedCount=resultDict['ProductMergedCount'],
                    SaleProductCount=resultDict['SaleProductCount'], TotalProductCount=resultDict['TotalProductCount'],
                    DownloadThreadCount=resultDict['DownloadThreadCount'], WarningCount=resultDict['WarningCount'],
                    ErrorCount=resultDict['ErrorCount'],
                    ProductWithProductSizeCount=resultDict['ProductWithProductSizeCount'],
                    ProductSizeAvailableCount=resultDict['ProductSizeAvailableCount'],
                    ProductSizeWithColorCount=resultDict['ProductSizeWithColorCount'],
                    TotalProductSizeCount=resultDict['TotalProductSizeCount'],
                    ScrapThreadCount=resultDict['ScrapThreadCount'],
                    ProductWithBrandCount=resultDict['ProductWithBrandCount'],
                    UniqueBrandCount=resultDict['UniqueBrandCount'],
                    DateCreated=resultDict['DateCreated'], MachineNo=resultDict['MachineNo']).save()


def SaveScrapTypes(scrapTypes):
    for typeDict in scrapTypes:
        ProductSize(Id=typeDict['Id'], ProductId=typeDict['ProductId'], Code=typeDict['Code'],
                    Name=typeDict['Name'], MachineNo=typeDict['MachineNo']).save()


def SaveStores(stores):
    for storeDict in stores:
        Store(Id=storeDict['Id'], Name=storeDict['Name'], Url=storeDict['Url'], AffiliateUrl=storeDict['AffiliateUrl'],
              Description=storeDict['Description'], ScrapperClassName=storeDict['ScrapperClassName'],
              AUSite=storeDict['AUSite'], NZSite=storeDict['NZSite'], USSite=storeDict['USSite'],
              MergeProductSize=storeDict['MergeProductSize'], ScrapThreadCount=storeDict['ScrapThreadCount'],
              DownloadThreadCount=storeDict['DownloadThreadCount'], NoReferrer=storeDict['NoReferrer'],
              Hidden=storeDict['Hidden'], DateCreated=storeDict['DateCreated'], DateUpdated=storeDict['DateUpdated'],
              MachineNo=storeDict['MachineNo']).save()


def ShowException(e):
    return traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
