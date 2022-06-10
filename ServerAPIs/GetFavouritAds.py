import json
import os
import sys

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ServerAPIs.models import *


@api_view(['POST'])
@csrf_exempt
def get_Favourits_Ads(request):
    userJson = json.loads(json.dumps(request.data))
    try:
        uId = userJson['user_id']
        favourits_Ads = Favourite_Ads.objects.filter(user_id=uId)
    except Exception as e:
        context = {'Status': False, 'Message': 'Error getting filter types'}
        ShowException(e)
        return Response(context)

    if not favourits_Ads:
        context = {'Status': False, 'Message': 'No Favourite Ads found'}
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
        # favourits_Ad_list = []
        # for favourits_Ad in favourits_Ads:
        #     data = {
        #         "user_id": favourits_Ad.user_id.id,
        #         "created_at": favourits_Ad.created_at,
        #         "id": favourits_Ad.product_id.id,
        #         "product": {
        #             "id": favourits_Ad.product_id.id,
        #             "name": favourits_Ad.product_id.name,
        #             "url": favourits_Ad.product_id.product_url,
        #             "brand": favourits_Ad.product_id.brand,
        #             "store": favourits_Ad.product_id.store_name,
        #             "price": favourits_Ad.product_id.price,
        #             "price_highest": favourits_Ad.product_id.price_highest,
        #             "sale_price": favourits_Ad.product_id.sale_price,
        #             "sale_price_highest": favourits_Ad.product_id.sale_price_highest,
        #             "image": favourits_Ad.product_id.image,
        #             "display_color": favourits_Ad.product_id.display_color,
        #             "created_at": favourits_Ad.product_id.created_at,
        #             "regular_size": favourits_Ad.product_id.regular_size,
        #             "petite_size": favourits_Ad.product_id.petite_size,
        #             "plus_size": favourits_Ad.product_id.plus_size,
        #             "tall_size": favourits_Ad.product_id.tall_size,
        #         }
        #     }
        #     favourits_Ad_list.append(data)
        favourits_Ad_list = get_Fav_List(favourits_Ads)
        favourits_Ads = favourits_Ad_list[startlimit:endlimit]
        data = {"data": favourits_Ads, "Total_Favourite_Ads": len(favourits_Ad_list), "Status": True,
                "Message": "Favourite Ads against User ID..!"}

        return Response(data=data)
    except Exception as e:
        context = {'Status': False, 'Message': 'Error While Sending data'}
        ShowException(e)
        return Response(context)


def get_Fav_List(favourits_Ads):
    favourits_Ad_list = []
    for favourits_Ad in favourits_Ads:
        data = {
            "user_id": favourits_Ad.user_id.id,
            "created_at": favourits_Ad.created_at,
            "id": favourits_Ad.product_id.id,
            "product": {
                "id": favourits_Ad.product_id.id,
                "name": favourits_Ad.product_id.name,
                "url": favourits_Ad.product_id.product_url,
                "brand": favourits_Ad.product_id.brand,
                "store": favourits_Ad.product_id.store_name,
                "price": favourits_Ad.product_id.price,
                "price_highest": favourits_Ad.product_id.price_highest,
                "sale_price": favourits_Ad.product_id.sale_price,
                "sale_price_highest": favourits_Ad.product_id.sale_price_highest,
                "image": favourits_Ad.product_id.image,
                "display_color": favourits_Ad.product_id.display_color,
                "created_at": favourits_Ad.product_id.created_at,
                "regular_size": favourits_Ad.product_id.regular_size,
                "petite_size": favourits_Ad.product_id.petite_size,
                "plus_size": favourits_Ad.product_id.plus_size,
                "tall_size": favourits_Ad.product_id.tall_size,
            }
        }
        favourits_Ad_list.append(data)
    return favourits_Ad_list


def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
