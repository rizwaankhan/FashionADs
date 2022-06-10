import json
import os
import sys

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ServerAPIs.models import *


@api_view(['POST'])
@csrf_exempt
def articleDetail(request):
    try:
        articalJson = json.loads(json.dumps(request.data))
    except Exception as e:
        context = {'Message': 'Error While Getting Article Data', 'Status': False}
        ShowException(e)
        return Response(context)
    try:
        article = Articles.objects.get(id=articalJson.get('article_id'))
    except Exception as e:
        context = {'Message': 'Article Not Found', 'Status': False}
        ShowException(e)
        return Response(context)
    try:
        comments = Article_Comments.objects.filter(article_id=article.id)
        data = {
            "product_id": 1,
            "title": article.title,
            "author": article.author,
            "description": article.description,
            "css": article.css,
            "keywords": article.keywords,
            "comment": GetComments(comments)}
        context = {"data": data, 'Message': 'Article Detail',
                   'Status': True}
        return Response(context)

    except Exception as e:
        context = {'Message': 'Error While Saving Blog ', 'Status': False}
        ShowException(e)
        return Response(context)


def GetComments(comments):
    commentList = []
    for comment in comments:
        data = {
            "username": comment.user_id.display_name,
            "comment": comment.comment_text
        }
        commentList.append(data)
    return commentList


def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
