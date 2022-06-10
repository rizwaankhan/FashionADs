import datetime
import json
import os
import traceback

import django
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FashionADs.settings")
django.setup()
from ServerAPIs.models import *

requestHeader = {'Content-Type': 'application/json'}
domainAndUrl = 'https://51ef-2407-aa80-314-945d-30a8-6dbe-1259-66.ngrok.io/api/'


def PostMatchedProAPI():
    print('Getting Matched Products')

    matchedData = list(ProductMatched.objects.values())[:2]
    if not matchedData:
        return

    while len(matchedData) != 0:
        PostToServer(domainAndUrl + 'save_matched_products', matchedData[:1])
        del matchedData[0:1]

    print('Saved Matched Products Successfully')


def PostToServer(reqUrl, reqJson):
    try:
        reqJson = json.dumps(reqJson, default=default)
        print(reqJson)
        saveData = requests.post(url=reqUrl, data=reqJson, headers=requestHeader)
        print(saveData.content)
    except Exception as e:
        print(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
        pass


def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


if __name__ == '__main__':
    PostMatchedProAPI()
