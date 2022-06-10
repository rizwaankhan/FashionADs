import json
import os
import sys

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ServerAPIs.models import *


@api_view(['POST'])
@csrf_exempt
def articles(request):
    try:
        articalJson = json.loads(json.dumps(request.data))
    except Exception as e:
        context = {'Message': 'Error While Getting Blog Data', 'Status': False}
        ShowException(e)
        return Response(context)
    try:
        Articles(title=articalJson.get('title'), description=articalJson.get('description'),
                 css=articalJson.get('css'),
                 keywords=articalJson.get('keywords'), product_id=articalJson.get('product_id'),
                 author=articalJson.get('author')).save()

        context = {'Message': 'Your Artical Posted Successfully.','Status': True}
        return Response(context)

    except Exception as e:
        context = {'Message': 'Error While Saving Artical ', 'Status': False}
        ShowException(e)
        return Response(context)


def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
