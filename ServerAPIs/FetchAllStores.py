import json
import traceback
from django.views.decorators.csrf import csrf_exempt
from ServerAPIs.models import *
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
@csrf_exempt
def fetch_all_stores(request):
    try:
        storesData = list(Stores.objects.values())
    except Exception as e:
        context = {'Error': 'Error getting stores', 'return_data': []}
        ShowException(e)
        return Response(context)

    if not storesData:
        context = {'Error': 'Stores not found', 'return_data': []}
        return Response(context)

    try:
        storesJson = json.loads(json.dumps(storesData, indent=4, sort_keys=True, default=str))
    except Exception as e:
        context = {'Error': 'Error getting stores data', 'return_data': []}
        ShowException(e)
        return Response(context)

    return Response(storesJson)


def ShowException(e):
    return traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
