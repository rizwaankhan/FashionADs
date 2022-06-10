import json
import os
import sys

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ServerAPIs.models import *


@api_view(['POST'])
@csrf_exempt
def userInformation(request):
    userJson = json.loads(json.dumps(request.data))
    try:
        existingUser = userJson.get('user_id')
        user = Users.objects.get(id=existingUser)
    except Exception as e:
        context = {'Message': 'Error getting Users Data', 'Status': False}
        ShowException(e)
        return Response(context)
    try:
        context = {
            "data":
                {"id": user.id,
                 "first_name": user.first_name,
                 "last_name": user.last_name,
                 "image": user.display_image,
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
            "Message": 'Profile information...!'
        }
        return Response(context)
    except Exception as e:
        context = {'Message': 'Error While Getting Users Data..!', 'Status': False}
        ShowException(e)
        return Response(context)


def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
