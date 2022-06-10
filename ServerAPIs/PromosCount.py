import ast
import json
import sys, os, operator
import traceback

from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from ServerAPIs.models import *
from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from functools import reduce
from django.db import connection
from py_linq import Enumerable


@api_view(['Get'])
@csrf_exempt
def promos_count(request):
    try:
        context = {
            "Deal": Products.objects.filter(promo_offer_type__icontains='Deal').count(),
            "New Arrival": Products.objects.filter(promo_offer_type__icontains='New Arrival').count(),
            "Sales": Products.objects.filter(promo_offer_type__icontains='Sales').count(),
            "Clearance": Products.objects.filter(promo_offer_type__icontains='Clearance').count(),
            "Weekly Ad": Products.objects.filter(promo_offer_type__icontains='Weekly Ad').count(),
            "Today\'s Ad": Products.objects.filter(promo_offer_type__icontains="Today\'s Ad").count(),
            "Price Match": Products.objects.filter(price_offer_type__icontains='Price Match').count(),
            "Price Guarantee": Products.objects.filter(price_offer_type__icontains='Price Guarantee').count(),
            "Free Shipping": Products.objects.filter(shipping_offer_label__iregex='Free\s\w+\sShipping').count(),
            "Shipping Code": Products.objects.filter(shipping_offer_type__icontains='Shipping Code').count(),
            "Free Return": Products.objects.filter(shipping_offer_label__icontains='Free Return').count(),
            "Free Exchange": Products.objects.filter(shipping_offer_label__icontains='Free Exchange').count(),
            "Delivery Time": Products.objects.filter(shipping_offer_type__icontains='Delivery Time').count(),
            "Store Pickup": Products.objects.filter(shipping_offer_type__icontains='Store Pickup').count(),
            "Shipping Type": Products.objects.filter(shipping_offer_type__icontains='Shipping Type').count(),
            "Cash Back": Products.objects.filter(other_offer_type__icontains='Cash Back').count(),
            "Coupon Codes": Products.objects.filter(other_offer_type__icontains='Coupon Codes').count(),
            "BOGO": Products.objects.filter(other_offer_type__icontains='BOGO').count(),
            "Signup Reward": Products.objects.filter(other_offer_type__icontains='Signup Reward').count(),
            "Referral": Products.objects.filter(other_offer_type__icontains='Referral').count(),
            "Membership": Products.objects.filter(other_offer_type__icontains='Membership').count(),
            "App Download": Products.objects.filter(other_offer_type__icontains='App Download').count(),
            "Youth Discount": Products.objects.filter(other_offer_type__icontains='Youth Discount').count(),
            "Student Discount": Products.objects.filter(other_offer_type__icontains='Student Discount').count(),
            "Military Discount": Products.objects.filter(other_offer_type__icontains='Military Discount').count(),
            "Worker Discount": Products.objects.filter(other_offer_type__icontains='Worker Discount').count(),
            "Credit Card Member": Products.objects.filter(other_offer_type__icontains='Credit Card Member').count(),
            "Gift Cards": Products.objects.filter(other_offer_type__icontains='Gift Cards').count(),
            "Gift Products": Products.objects.filter(other_offer_type__icontains='Gift Products').count(),
        }
    except Exception as e:
        context = {'Error': 'Error getting promotions data', 'return_data': []}
        print(ShowException(e))
        return Response(context)

    return Response(context)


def ShowException(e):
    return traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
