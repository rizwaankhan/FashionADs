import json
import os
import sys

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ServerAPIs.models import *


@api_view(['POST'])
@csrf_exempt
def userEmailAlert(request):
    # Get All store, brand, category and product alerts for a user.
    global data
    userJson = json.loads(json.dumps(request.data))
    try:
        uId = userJson['user_id']
        emailAlerts = Email_Alerts.objects.filter(user_id=uId)
    except Exception as e:
        context = {'Status': False, 'Message': 'Error getting Alerts'}
        ShowException(e)
        return Response(context)

    if not emailAlerts:
        context = {'Status': False, 'Message': 'No Ads Alert found'}
        return Response(context)

    try:
        page = int(userJson['page'])
        page = 1 if page == 0 else page
    except:
        page = 1

    try:
        perPage = int(userJson['per_page'])
        perPage = 1 if perPage == 0 else perPage
    except:
        perPage = 40


    try:
        endlimit = page * perPage
        startlimit = endlimit - perPage
        email_alert_list = get_Fav_List(emailAlerts)
        email_alert = email_alert_list[startlimit:endlimit]
        data = {"data": email_alert, "totalAlert": len(email_alert_list), "Status": True,
                "Message": "Alerts against User ID..!"}

        return Response(data=data)
    except Exception as e:
        context = {'Status': False, 'Message': 'Error While Sending data'}
        ShowException(e)
        return Response(context)


def get_Fav_List(emailAlerts):
    favourits_Ad_list = []
    for emailAlert in emailAlerts:
        if emailAlert.product_id:
            data = {
                "user_id": emailAlert.user_id.id,
                "user_name": emailAlert.user_id.first_name,
                "created_at": emailAlert.created_at,
                "alert_type": emailAlert.alert_type,
                "email_address": emailAlert.email_address,
                "name": emailAlert.name,
                "alert_nature": emailAlert.alert_nature,
                "alert_status": emailAlert.alert_status,
                "id": emailAlert.id,
                "product": {
                    "product_id": Products.objects.get(id=emailAlert.product_id.id).id,
                    "name": Products.objects.get(id=emailAlert.product_id.id).name,
                }
            }
            favourits_Ad_list.append(data)
        elif emailAlert.parent_category_id:
            data = {
                "user_id": emailAlert.user_id.id,
                "user_name": emailAlert.user_id.first_name,
                "created_at": emailAlert.created_at,
                "alert_type": emailAlert.alert_type,
                "email_address": emailAlert.email_address,
                "name": emailAlert.name,
                "alert_nature": emailAlert.alert_nature,
                "alert_status": emailAlert.alert_status,
                "id": emailAlert.id,
                "parent_category": {
                    "parent_category_id": emailAlert.parent_category_id,
                    "parent_category_name": Parent_Categories.objects.get(
                        id=emailAlert.parent_category_id).parent_category_name,
                },
            }
            favourits_Ad_list.append(data)
            # data = {"data": favourits_Ad_list, "Status": True,
            #         "Message": "Alerts against User ID..!"}
        elif emailAlert.our_category_id:
            data = {
                "user_id": emailAlert.user_id.id,
                "user_name": emailAlert.user_id.first_name,
                "created_at": emailAlert.created_at,
                "alert_type": emailAlert.alert_type,
                "email_address": emailAlert.email_address,
                "name": emailAlert.name,
                "alert_nature": emailAlert.alert_nature,
                "alert_status": emailAlert.alert_status,
                "id": emailAlert.id,
                "our_category": {
                    "our_category_id": emailAlert.our_category_id,
                    "our_category_name": Our_Categories.objects.get(id=emailAlert.our_category_id).category_name
                },
            }
            favourits_Ad_list.append(data)
            # data = {"data": favourits_Ad_list, "Status": True,
            #         "Message": "Alerts against User ID..!"}
        elif emailAlert.store_id:
            data = {
                "user_id": emailAlert.user_id.id,
                "user_name": emailAlert.user_id.first_name,
                "created_at": emailAlert.created_at,
                "alert_type": emailAlert.alert_type,
                "email_address": emailAlert.email_address,
                "name": emailAlert.name,
                "alert_nature": emailAlert.alert_nature,
                "alert_status": emailAlert.alert_status,
                "id": emailAlert.id,
                "store": {
                    "store_id": Stores.objects.get(id=emailAlert.store_id).id,
                    "store_name": Stores.objects.get(id=emailAlert.store_id).store_name,
                    # "brand": stores.objects.get(Id=emailAlert.store_id).nature
                },
            }
            favourits_Ad_list.append(data)
            # data = {"data": favourits_Ad_list, "Status": True,
            #         "Message": "Alerts against User ID..!"}
    return favourits_Ad_list



def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
