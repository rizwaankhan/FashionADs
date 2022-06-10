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


def PostSimilarProAPI():
    print('Getting Similar Products')

    similarData = list(ProductSimilarity.objects.values())[:10]
    if not similarData:
        return

    while len(similarData) != 0:
        PostToServer(domainAndUrl + 'save_similar_products', similarData[:5])
        del similarData[0:5]

    print('Saved Similar Products Successfully')


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
    PostSimilarProAPI()
