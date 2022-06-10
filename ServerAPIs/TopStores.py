import ast
import json
import sys, os, operator
import traceback

from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated

from ServerAPIs.models import *
from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from functools import reduce
from django.db import connection
from py_linq import Enumerable


# @permission_classes((IsAuthenticated,))
@api_view(['GET'])
@csrf_exempt
def top_stores(request):
    try:
        idsList = []
        promoList = ['Coupon Codes', 'discount_percentage', 'Free Shipping', 'Gift Cards', 'Deal', 'New Arrival',
                     'Sales', 'Clearance', 'Price Match', 'Price Guarantee', 'Free Return', 'Free Exchange',
                     'Store Pickup']

        allStores = Stores.objects.filter(nature='Store').all()
        for promo in promoList:
            if len(idsList) == 12:
                break

            if promo == 'discount_percentage':
                for store in allStores:
                    if len(idsList) == 12:
                        break

                    discounts = list(filter(None, Products.objects.filter(store_id=store.id).values_list(promo,
                                                                                                         flat=True).distinct()))
                    if discounts:
                        Stores.objects.filter(id=store.id).update(discount_percentage=float(max(discounts, key=float)))
                        idsList.append(store.id)
            else:
                idsList.extend(list(allStores.filter(promotions__contains=promo).values_list('id', flat=True)))

        idsList = reduce(lambda l, x: l.append(x) or l if x not in l else l, idsList, [])
    except Exception as e:
        context = {'Error': 'Error getting stores', 'return_data': []}
        print(ShowException(e))
        return Response(context)

    try:
        storesData = []
        for id in idsList:
            store = Stores.objects.get(id=id)
            if store.promotions is None:
                promoDict = {}
            else:
                promoDict = eval(store.promotions)

            if float(store.discount_percentage) == 0.0:
                discount_percentage = ""
            else:
                discount_percentage = "UPTO " + str(int(store.discount_percentage)) + "% OFF"

            context = {
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
            storesData.append(context)
    except Exception as e:
        context = {'Error': 'Error getting stores data', 'return_data': []}
        print(ShowException(e))
        return Response(context)

    return Response(storesData)


def ShowException(e):
    return traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
