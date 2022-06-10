import json
import traceback
from django.views.decorators.csrf import csrf_exempt
from ServerAPIs.models import *
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
@csrf_exempt
def fetch_all_categories(request):
    try:
        categoriesData = list(Our_Categories.objects.values())
    except Exception as e:
        context = {'Error': 'Error getting categories', 'return_data': []}
        ShowException(e)
        return Response(context)

    if not categoriesData:
        context = {'Error': 'Categories not found', 'return_data': []}
        return Response(context)

    try:
        categoriesJson = json.loads(json.dumps(categoriesData, indent=4, sort_keys=True, default=str))
    except Exception as e:
        context = {'Error': 'Error getting categories data', 'return_data': []}
        ShowException(e)
        return Response(context)

    return Response(categoriesJson)


def ShowException(e):
    return traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)