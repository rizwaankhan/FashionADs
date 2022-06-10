import json
import os
import sys

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.templatetags.rest_framework import data

from ServerAPIs.models import *


@api_view(['POST'])
@csrf_exempt
def login_Api(request):
    userJson = json.loads(json.dumps(request.data))
    if request.method == 'POST':
        email = userJson['email']
        password = userJson['password']
        try:
            user = Users.objects.get(email=email)
            if user.password == password:
                context = {"data": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "state": user.state,
                    "city": user.city,
                    "zip_code": user.zip_code,
                    "street_address": user.street_address,
                    "gender": user.gender,
                    "latitude": user.latitude,
                    "longitude": user.longitude,
                },
                    "Status": True,
                    "Message": 'Successfully Login',
                }
            else:
                context = {"data": {},
                           "Status": False,
                           "Message": "Password doesn't match..!",
                           }
            return Response(context)
        except Exception as e:
            context = {"data": {},
                       "Status": False,
                       "Message": 'Error While Getting User info or User Dose Not Exist..!'}
            ShowException(e)
            return Response(context)
def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
