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
def GetMatchedProductFilter(request):
    userJson = json.loads(json.dumps(request.data))
    try:
        parentProductID = userJson['parent_product_id']
        productID = userJson['product_id']
        matchedProduct = ProductMatched.objects.get(ParentProductId=parentProductID, ProductId=productID)
    except Exception as e:
        context = {'Status': False, 'Message': 'Error while getting Matched Products Filters'}
        ShowException(e)
        return Response(context)

    if not matchedProduct:
        context = {'Status': False, 'Message': 'No Matched Products Filters found'}
        return Response(context)

    try:
        data = {
            "parent_product_id": matchedProduct.ParentProductId,
            "product_id": matchedProduct.ProductId.id,
            "matched_percentage": matchedProduct.MatchedPercentage,
            "character": matchedProduct.Character,
            "closure": matchedProduct.Closure,
            "dress_length": matchedProduct.DressLength,
            "dress_style": matchedProduct.DressStyle,
            "embellishment": matchedProduct.Embellishment,
            "feature": matchedProduct.Feature,
            "fit_type": matchedProduct.FitType,
            "garment_care": matchedProduct.GarmentCare,
            "material": matchedProduct.Material,
            "neckline": matchedProduct.Neckline,
            "occasion": matchedProduct.Occasion,
            "pattern": matchedProduct.Pattern,
            "fastening_type": matchedProduct.FasteningType,
            "cuff_style": matchedProduct.CuffStyle,
            "collar": matchedProduct.Collar,
            "sleeve_length": matchedProduct.SleeveLength,
            "sleeve_type": matchedProduct.SleeveType,
            "themes": matchedProduct.Themes,
            "season": matchedProduct.Season
        }
        data = dict(filter(itemgetter(1), data.items()))
        data = {"data": data, "Status": True,
                "Message": "Matched Products Filters Against Product ID..!"}

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
