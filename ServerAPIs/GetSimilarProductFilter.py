import json
import os
import sys
from operator import itemgetter

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ServerAPIs.models import *


@api_view(['POST'])
@csrf_exempt
def get_similar_product_filter(request):
    userJson = json.loads(json.dumps(request.data))
    try:
        parentProductID = userJson['parent_product_id']
        productID = userJson['product_id']
        similarProduct = ProductSimilarity.objects.get(ParentProductId=parentProductID, ProductId=productID)
    except Exception as e:
        context = {'Status': False, 'Message': 'Error while getting Similar Products Filters'}
        ShowException(e)
        return Response(context)

    if not similarProduct:
        context = {'Status': False, 'Message': 'No Similar Products Filters found'}
        return Response(context)

    try:
        data = {
            "character": similarProduct.Character,
            "closure": similarProduct.Closure,
            "dress_length": similarProduct.DressLength,
            "dress_style": similarProduct.DressStyle,
            "embellishment": similarProduct.Embellishment,
            "feature": similarProduct.Feature,
            "fit_type": similarProduct.FitType,
            "garment_care": similarProduct.GarmentCare,
            "material": similarProduct.Material,
            "neckline": similarProduct.Neckline,
            "occasion": similarProduct.Occasion,
            "pattern": similarProduct.Pattern,
            "fastening_type": similarProduct.FasteningType,
            "cuff_style": similarProduct.CuffStyle,
            "collar": similarProduct.Collar,
            "sleeve_length": similarProduct.SleeveLength,
            "sleeve_type": similarProduct.SleeveType,
            "themes": similarProduct.Themes,
            "season": similarProduct.Season
        }
        data = dict(filter(itemgetter(1), data.items()))
        data = {"data": data, "Status": True,
                "Message": "Similar Products Filters Against Product ID..!"}
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
