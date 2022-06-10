import json
import os
import sys

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ServerAPIs.models import *


@api_view(['POST'])
@csrf_exempt
def get_matched_products(request):
    userJson = json.loads(json.dumps(request.data))
    try:
        productID = userJson['product_id']
        matchedProductObjs = ProductMatched.objects.filter(ParentProductId=productID)
    except Exception as e:
        context = {'Status': False, 'Message': 'Error while getting Matched Products'}
        ShowException(e)
        return Response(context)

    if not matchedProductObjs:
        context = {'Status': False, 'Message': 'No Matched Products found'}
        return Response(context)

    try:
        matchedProductList = []
        for matchedProduct in matchedProductObjs:
            data = {
                "matched_percentage": matchedProduct.MatchedPercentage,
                "product": {
                    "id": matchedProduct.ProductId.id,
                    "name": matchedProduct.ProductId.name,
                    "brand": matchedProduct.ProductId.brand,
                    "price": matchedProduct.ProductId.price,
                    "sale_price": matchedProduct.ProductId.sale_price,
                    "image": str(matchedProduct.ProductId.image).split(',')[0],
                    "display_color": matchedProduct.ProductId.display_color
                }
            }
            matchedProductList.append(data)
        data = {"data": matchedProductList, "Status": True,
                "Message": "Matched Products Against Product ID..!"}

        return Response(data=data)
    except Exception as e:
        context = {'Status': False, 'Message': 'Error While Sending data'}
        ShowException(e)
        return Response(context)


def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
