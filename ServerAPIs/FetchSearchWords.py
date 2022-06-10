import itertools
import json
import os
import sys

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ServerAPIs.models import *


@api_view(['GET'])
@csrf_exempt
def fetch_search_words(request):
    try:
        keywords = []

        categories = list(filter(None, set(list(Our_Categories.objects.values_list('category_name', flat=True)))))
        age = list(filter(None, set(list(Our_Categories.objects.values_list('age', flat=True)))))
        catKeywords = list(filter(None, set(list(Our_Categories.objects.values_list('keywords', flat=True)))))
        for keyword in catKeywords:
            if keyword:
                if ', ' in str(keyword):
                    keywords.extend(keyword.split(', '))
                if ',' in str(keyword):
                    keywords.extend(keyword.split(','))
                else:
                    keywords.extend([keyword])

        filters = list(filter(None, set(list(Our_Filters.objects.values_list('filter_name', flat=True)))))
        filterKeywords = list(filter(None, set(list(Our_Filters.objects.values_list('keywords', flat=True)))))
        for keyword in filterKeywords:
            if keyword:
                if ', ' in str(keyword):
                    keywords.extend(keyword.split(', '))
                if ',' in str(keyword):
                    keywords.extend(keyword.split(','))
                else:
                    keywords.extend([keyword])

        allWords = list(map(lambda x: str(x).strip(), list(set(age + categories + filters + keywords))))
    except Exception as e:
        context = {'Error': 'Error getting Keywords', 'return_data': []}
        ShowException(e)
        return Response(context)

    if not allWords:
        context = {'Error': 'Keywords not found', 'return_data': []}
        return Response(context)

    try:
        KeyWordsAndFilters = json.loads(json.dumps(allWords, indent=4, sort_keys=True, default=str))
    except Exception as e:
        context = {'Error': 'Error getting Keywords ', 'return_data': []}
        ShowException(e)
        return Response(context)

    return Response(KeyWordsAndFilters)


def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
