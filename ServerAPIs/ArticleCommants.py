import json
import os
import sys

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ServerAPIs.models import *


@api_view(['POST'])
@csrf_exempt
def article_commants(request):
    try:
        articalJson = json.loads(json.dumps(request.data))
    except Exception as e:
        context = {'Message': 'Error While Getting Article Data', 'Status': False}
        ShowException(e)
        return Response(context)
    try:
        article = Articles.objects.get(id=articalJson.get('article_id'))
        if article:
            user_object = Users.objects.get(id=articalJson.get('user_id'))
            if user_object:
                print(articalJson.get('comment'))
                Article_Comments(user_id=user_object, article_id=article,
                                 comment_text=articalJson.get('comment')).save()
                context = {'Message': 'Congrats You Made a Comment.',
                           'Status': True}
                return Response(context)
            else:
                context = {'Message': 'User Not Found..!',
                           'Status': False}
                return Response(context)
    except Exception as e:
        context = {'Message': 'Error While Saving Article Comment ', 'Status': False}
        ShowException(e)
        return Response(context)


def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
