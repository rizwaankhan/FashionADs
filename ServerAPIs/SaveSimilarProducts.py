import datetime
import json
import re
import sys, os, operator
import traceback

import unidecode as unidecode
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from ServerAPIs.models import *
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from functools import reduce
from django.db import connection
from py_linq import Enumerable


@api_view(['POST'])
@csrf_exempt
def save_similar_products(request):
    try:
        similarJson = json.loads(json.dumps(request.data))
    except Exception as e:
        ex = ShowException(e)
        context = {'Error': 'Error getting similar data: ' + str(ex), 'return_data': []}
        return Response(context)

    saved = 0
    failed = 0
    for similarDict in similarJson:
        try:
            if ProductSimilarity.objects.filter(ProductId=similarDict['ProductId_id'], GroupId=similarDict['GroupId'],
                                                MachineNo=similarDict['MachineNo']).exists():
                ProductMatched.objects.filter(ProductId=similarDict['ProductId_id'], GroupId=similarDict['GroupId'],
                                              MachineNo=similarDict['MachineNo']).update(
                    ProductId=Products.objects.filter(id=similarDict['ProductId_id']).first(),
                    GroupId=similarDict['GroupId'], Character=similarDict['GroupId'], Closure=similarDict['Closure'],
                    DressLength=similarDict['DressLength'], DressStyle=similarDict['DressStyle'],
                    Embellishment=similarDict['Embellishment'], Feature=similarDict['Feature'],
                    FitType=similarDict['FitType'], GarmentCare=similarDict['GarmentCare'],
                    Material=similarDict['Material'], Neckline=similarDict['Neckline'],
                    Occasion=similarDict['Occasion'], Pattern=similarDict['Pattern'],
                    FasteningType=similarDict['FasteningType'], CuffStyle=similarDict['CuffStyle'],
                    Collar=similarDict['Collar'], SleveesLength=similarDict['SleveesLength'],
                    SleveesType=similarDict['SleveesType'], Themes=similarDict['Themes'], Season=similarDict['Season'],
                    ShowOnly=similarDict['ShowOnly'], MachineNo=similarDict['MachineNo']).save()
            else:
                ProductMatched(ProductId=Products.objects.filter(id=similarDict['ProductId_id']).first(),
                               GroupId=similarDict['GroupId'], Character=similarDict['GroupId'],
                               Closure=similarDict['Closure'], DressLength=similarDict['DressLength'],
                               DressStyle=similarDict['DressStyle'], Embellishment=similarDict['Embellishment'],
                               Feature=similarDict['Feature'], FitType=similarDict['FitType'],
                               GarmentCare=similarDict['GarmentCare'], Material=similarDict['Material'],
                               Neckline=similarDict['Neckline'], Occasion=similarDict['Occasion'],
                               Pattern=similarDict['Pattern'], FasteningType=similarDict['FasteningType'],
                               CuffStyle=similarDict['CuffStyle'], Collar=similarDict['Collar'],
                               SleveesLength=similarDict['SleveesLength'], SleveesType=similarDict['SleveesType'],
                               Themes=similarDict['Themes'], Season=similarDict['Season'],
                               ShowOnly=similarDict['ShowOnly'], MachineNo=similarDict['MachineNo']).save()
            saved += 1
        except Exception as e:
            failed += 1
            ex = ShowException(e)
            context = {'Error': 'Error saving similar data: ' + str(ex), 'return_data': []}
            return Response(context)
        continue

    context = {"flag": True, "total_saved": saved, "failed_to_save": failed}
    return Response(context)


def ShowException(e):
    return traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
