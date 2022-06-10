import json
import os
import sys

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ServerAPIs.models import *


@api_view(['POST'])
@csrf_exempt
def get_similar_products(request):
    userJson = json.loads(json.dumps(request.data))
    try:
        productID = userJson['product_id']
        similarProductObjs = ProductSimilarity.objects.filter(ParentProductId=productID)
    except Exception as e:
        context = {'Status': False, 'Message': 'Error while getting Similar Products'}
        ShowException(e)
        return Response(context)

    if not similarProductObjs:
        context = {'Status': False, 'Message': 'No Similar Products found'}
        return Response(context)

    try:
        similarProductList = []
        for similarProduct in similarProductObjs:
            data = {
                "product": {
                    "id": similarProduct.ProductId.id,
                    "url": similarProduct.ProductId.product_url,
                    "name": similarProduct.ProductId.name,
                    "price": similarProduct.ProductId.price,
                    "sale_price": similarProduct.ProductId.sale_price,
                    "image_url": similarProduct.ProductId.image,
                }
            }
            similarProductList.append(data)

        data = {"data": similarProductList, "Status": True,
                "Message": "Similar Products Against Product ID..!"}
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
