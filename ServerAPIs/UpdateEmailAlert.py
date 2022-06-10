import json
import os
import sys

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ServerAPIs.models import *


@api_view(['POST'])
@csrf_exempt
def updateEmailAlert(request):
    global data
    userJson = json.loads(json.dumps(request.data))
    try:
        alertID = userJson['update_id']
        emailAlert = Email_Alerts.objects.get(id=alertID)
    except Exception as e:
        context = {'Status': False, 'Message': 'Error While getting Alerts or No Ads Alert found..!'}
        ShowException(e)
        return Response(context)

    try:
        emailAlert.alert_nature = userJson["alert_nature"]
        emailAlert.alert_type = userJson["alert_type"]
        emailAlert.save()
        data = {"Status": True,
                "Message": "Alert Updated Successfully..!"}
        return Response(data)
    except Exception as e:
        context = {'Status': False, 'Message': 'Error While Updating data..!'}
        ShowException(e)
        return Response(context)


def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
