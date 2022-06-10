import csv
import datetime
import json
import os
import re
import sys
import traceback

from rest_framework.decorators import api_view
from rest_framework.response import Response
import unidecode

from ServerAPIs.models import *


@api_view(['POST'])
def saveCsvStore(request):
    if request.data != '':
        try:
            reqJson = json.loads(json.dumps(request.data))
            if Stores.objects.filter(store_name=reqJson['store_name'], nature=reqJson['nature']).exists():
                existingStoreUrl = Stores.objects.get(store_name=reqJson['store_name'],
                                                      nature=reqJson['nature']).store_url.rstrip('/')
                if existingStoreUrl == '' or existingStoreUrl is None:
                    Stores.objects.filter(store_name=reqJson['store_name'], nature=reqJson['nature']).update(
                        store_name=reqJson['store_name'], store_url=reqJson['store_url'], nature=reqJson['nature'],
                        promotions=reqJson['promos'])
                    return Response(data="Store Url Updated Successfully: Added/Updated Promotions")
                else:
                    Stores.objects.filter(store_name=reqJson['store_name'], nature=reqJson['nature']).update(
                        promotions=reqJson['promos'])
                    return Response(data="Store Already Exist: Added/Updated Promotions")
            else:
                newStore = Stores.objects.create(store_name=reqJson['store_name'], store_url=reqJson['store_url'],
                                                 nature=reqJson['nature'], promotions=reqJson['promos'])
                storeSlug = Slugify(reqJson['store_name']) + "-" + str(newStore.id)
                Stores.objects.filter(id=newStore.id).update(store_slug=storeSlug)
                return Response(data="Store Saved Successfully")
        except Exception as e:
            ShowException(e)
            return Response(data="Error", status=400)

    else:
        csvPath = ''
        csvFile = ''
        try:
            csvPath = str((os.path.dirname(os.path.abspath(__file__)))).split('\FashionAppAPI')[0]
            csvFile = open("FashionAPI/Stores.csv", "r")
        except:
            for root, dirs, files in os.walk(csvPath):
                for name in files:
                    if name == "Stores.csv":
                        csvFile = open(str(root) + "\\Stores.csv", "r")
        csvreader = csv.reader(csvFile)
        if csvreader:
            next(csvreader)
            for data in csvreader:
                storeInfo = tuple(data)
                try:
                    if Stores.objects.filter(store_name=storeInfo[0], store_url=storeInfo[1]).exists():
                        storeId = Stores.objects.get(store_name=storeInfo[0], store_url=storeInfo[1]).id
                        Stores.objects.filter(store_name=storeInfo[0], store_url=storeInfo[1]).update(
                            store_name=storeInfo[0], store_url=storeInfo[1], nature=storeInfo[2],
                            store_logo=storeInfo[3], products_count=Products.objects.filter(store_id=storeId).count(),
                            updated_at=datetime.datetime.now())
                        return Response(data="Store Updated Successfully")
                    else:
                        storeInstance = Stores.objects.create(store_name=storeInfo[0],
                                                              store_slug=str(storeInfo[0]).lower(),
                                                              store_url=storeInfo[1], nature=storeInfo[2],
                                                              store_logo=storeInfo[3])
                        Stores.objects.filter(id=storeInstance.id).update(
                            store_slug=storeInstance.store_name + '-' + str(storeInstance.id),
                            products_count=Products.objects.filter(store_id=storeInstance.id).count())
                        return Response(data="Store Saved Successfully")
                except Exception as e:
                    ShowException(e)
                    return Response(data="Error", status=400)

    return Response(data="OK", status=200)


def Slugify(text):
    text = unidecode.unidecode(text).lower()
    return re.sub(r'[\W_]+$', '', re.sub(r'[\W_]+', '-', text))


def ShowException(e):
    return traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
