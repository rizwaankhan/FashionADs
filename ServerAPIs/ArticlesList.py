import json
import os
import sys

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ServerAPIs.models import *


@api_view(['GET'])
@csrf_exempt
def articlesList(request):
    try:
        articles = Articles.objects.all()
    except Exception as e:
        context = {'Message': 'Article Not Found', 'Status': False}
        ShowException(e)
        return Response(context)
    try:
        articlesList = []
        for article in articles:
            data = {
                "title": article.title,
                "author": article.author,
                "keywords": article.keywords,
                "thumbnail": article.image,
                "publish_date": article.created_at
            }
            articlesList.append(data)
        context = {"data": articlesList, 'Message': 'Articles List ',
                   'Status': True}
        return Response(context)
    except Exception as e:
        context = {'Message': 'Error While Getting Article Information.. ', 'Status': False}
        ShowException(e)
        return Response(context)


def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
