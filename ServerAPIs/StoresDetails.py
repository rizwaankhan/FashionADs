import json
import os
import re
import sys

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ServerAPIs.models import *


@api_view(['POST'])
@csrf_exempt
def storeDetails(request):
    global allStores
    allStores = []
    allStoresList = ''
    fatchedStores = ''
    try:
        storeJson = json.loads(json.dumps(request.data))
    except Exception as e:
        context = {'Status': False, 'Message': 'Error Getting Store Data..!'}
        print(ShowException(e))
        return Response(context)

    try:
        page = int(storeJson['page'])
        page = 1 if page == 0 else page
    except:
        page = 1

    try:
        perPage = int(storeJson['per_page'])
        perPage = 1 if perPage == 0 else perPage
    except:
        perPage = 40

    if not storeJson:
        context = {'Status': False, 'Message': 'No Store Data Found..!'}
        return Response(context)
    else:
        try:
            storeKey = storeJson.get('key')
            print(storeKey)
            if re.search('all', storeKey, re.I):
                endlimit = page * perPage
                startlimit = endlimit - perPage
                storesList = Stores.objects.filter(nature='Store')
                if storesList:
                    allStoresList = get_store_info(storesList)
                    storesList = allStoresList[startlimit:endlimit]
                    data = {"data": storesList, "Status": True,
                            "Message": "Stores That Start With Digit ..!",
                            "totalStores": len(allStoresList),
                            "fatchedStores": len(storesList),
                            "page": page}
                    return Response(data)
                else:
                    context = {'Status': False, 'Message': 'No Store Found '}
                    return Response(context)
            elif re.search(r'^[A-Z]', storeKey, re.I):
                endlimit = page * perPage
                startlimit = endlimit - perPage
                storesList = Stores.objects.filter(nature='Store', store_name__istartswith=storeJson['key'])
                if storesList:
                    allStoresList = get_store_info(storesList)
                    storesList = allStoresList[startlimit:endlimit]
                    data = {"data": storesList, "Status": True,
                            "Message": "Stores That Start With Alphabet ..!",
                            "totalStores": len(allStoresList),
                            "fatchedStores": len(storesList),
                            "page": page}
                    return Response(data)
                else:
                    context = {'Status': False, 'Message': 'No Store Found with : ' + str(storeJson['key'])}
                    return Response(context)
            elif re.search(r'^[0-9]', storeKey):
                digitList = []
                # ======= Pagination =======#
                endlimit = page * perPage
                startlimit = endlimit - perPage
                # ===== End Pagination ====#

                if '-' in storeKey:
                    ranges = str(storeKey).split('-')
                    start, end = int(ranges[0]), int(ranges[1])
                    if start < end:
                        digitList.extend(range(start, end))
                        digitList.append(end)
                    for digit in digitList:
                        storesList = Stores.objects.filter(nature='Store', store_name__startswith=str(digit))
                        if not storesList:
                            continue
                        else:
                            allStoresList = get_store_info(storesList)
                            fatchedStores = allStoresList[startlimit:endlimit]
                else:
                    storesList = Stores.objects.filter(nature='Store', store_name__startswith=str(storeKey))
                    if storesList:
                        allStoresList = get_store_info(storesList)
                        fatchedStores = allStoresList[startlimit:endlimit]
                data = {"data": fatchedStores, "Status": True,
                        "Message": "Stores That Start With Digit ..!",
                        "totalStores": len(allStoresList),
                        "fatchedStores": len(fatchedStores),
                        "page": page}
                return Response(data)

        except Exception as e:
            context = {'Status': False, 'Message': 'Error While Getting data'}
            print(ShowException(e))
            return Response(context)


def get_store_info(storesList):
    for store in storesList:
        if store.promotions is None:
            promoDict = {}
        else:
            promoDict = eval(store.promotions)

        discounts = list(filter(None, Products.objects.filter(store_id=store.id).values_list('discount_percentage',
                                                                                             flat=True).distinct()))
        if discounts:
            floatDiscount = float(max(discounts, key=float))
            discount_percentage = "UPTO " + str(int(floatDiscount)) + "% OFF"
        else:
            discount_percentage = ""

        data = {
            "id": store.id,
            "store_name": store.store_name,
            "store_logo": store.store_logo,
            "products_count": Products.objects.filter(store_id=store.id).count(),
            "coupon_codes": str(promoDict.get('Coupon Codes')).replace('None', ""),
            "discount_percentage": discount_percentage,
            "free_shipping": str(promoDict.get('Free Shipping')).replace('None', ""),
            "gift_cards": str(promoDict.get('Gift Cards')).replace('None', ""),
            "deal": str(promoDict.get('Deal')).replace('None', ""),
            "new_arrival": str(promoDict.get('New Arrival')).replace('None', ""),
            "sales": str(promoDict.get('Sales')).replace('None', ""),
            "clearance": str(promoDict.get('Clearance')).replace('None', ""),
            "price_match": str(promoDict.get('Price Match')).replace('None', ""),
            "price_guarantee": str(promoDict.get('Price Guarantee')).replace('None', ""),
            "free_return": str(promoDict.get('Free Return')).replace('None', ""),
            "free_exchange": str(promoDict.get('Free Exchange')).replace('None', ""),
            "store_pickup": str(promoDict.get('Store Pickup')).replace('None', "")
        }
        allStores.append(data)
    return allStores


def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
