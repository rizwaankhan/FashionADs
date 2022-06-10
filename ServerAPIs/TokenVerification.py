import json
import os
import sys

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ServerAPIs.models import *


@api_view(['POST'])
@csrf_exempt
def token_verify(request):
    userJson = json.loads(json.dumps(request.data))
    if userJson['reset_token'] and request.method == 'POST':
        try:
            user = Users.objects.get(reset_token=userJson['reset_token'])
            if user:
                context = {"data": {
                    "id": user.id,
                },
                    "Status": True,
                    "Message": 'Token Varified..!',
                }
                user.reset_token = ''
                user.save()
                return Response(context)
        except Exception as e:
            context = {"data": {},
                       "Status": False,
                       "Message": 'User Dose Not Exist or Token Expire..!', }
            ShowException(e)
            return Response(context)


def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
