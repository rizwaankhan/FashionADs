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
def save_matched_products(request):
    try:
        matchedJson = json.loads(json.dumps(request.data))
    except Exception as e:
        ex = ShowException(e)
        context = {'Error': 'Error getting matched data: ' + str(ex), 'return_data': []}
        return Response(context)

    saved = 0
    failed = 0
    for matchDict in matchedJson:
        try:
            if ProductMatched.objects.filter(ProductId=matchDict['ProductId_id'], GroupId=matchDict['GroupId'],
                                             MachineNo=matchDict['MachineNo']).exists():
                ProductMatched.objects.filter(ProductId=matchDict['ProductId_id'], GroupId=matchDict['GroupId'],
                                              MachineNo=matchDict['MachineNo']).update(
                    ProductId=Products.objects.filter(id=matchDict['ProductId_id']).first(),
                    GroupId=matchDict['GroupId'], Character=matchDict['GroupId'], Closure=matchDict['Closure'],
                    DressLength=matchDict['DressLength'], DressStyle=matchDict['DressStyle'],
                    Embellishment=matchDict['Embellishment'], Feature=matchDict['Feature'],
                    FitType=matchDict['FitType'], GarmentCare=matchDict['GarmentCare'], Material=matchDict['Material'],
                    Neckline=matchDict['Neckline'], Occasion=matchDict['Occasion'], Pattern=matchDict['Pattern'],
                    FasteningType=matchDict['FasteningType'], CuffStyle=matchDict['CuffStyle'],
                    Collar=matchDict['Collar'], SleveesLength=matchDict['SleveesLength'],
                    SleveesType=matchDict['SleveesType'], Themes=matchDict['Themes'], Season=matchDict['Season'],
                    MachineNo=matchDict['MachineNo']).save()
            else:
                ProductMatched(ProductId=Products.objects.filter(id=matchDict['ProductId_id']).first(),
                               GroupId=matchDict['GroupId'], Character=matchDict['GroupId'],
                               Closure=matchDict['Closure'], DressLength=matchDict['DressLength'],
                               DressStyle=matchDict['DressStyle'], Embellishment=matchDict['Embellishment'],
                               Feature=matchDict['Feature'], FitType=matchDict['FitType'],
                               GarmentCare=matchDict['GarmentCare'], Material=matchDict['Material'],
                               Neckline=matchDict['Neckline'], Occasion=matchDict['Occasion'],
                               Pattern=matchDict['Pattern'], FasteningType=matchDict['FasteningType'],
                               CuffStyle=matchDict['CuffStyle'], Collar=matchDict['Collar'],
                               SleveesLength=matchDict['SleveesLength'], SleveesType=matchDict['SleveesType'],
                               Themes=matchDict['Themes'], Season=matchDict['Season'],
                               MachineNo=matchDict['MachineNo']).save()
            saved += 1
        except Exception as e:
            failed += 1
            ex = ShowException(e)
            context = {'Error': 'Error saving matched data: ' + str(ex), 'return_data': []}
            return Response(context)
        continue

    context = {"flag": True, "total_saved": saved, "failed_to_save": failed}
    return Response(context)


def ShowException(e):
    return traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
