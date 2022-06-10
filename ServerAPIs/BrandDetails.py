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
def brandDetails(request):
    global allBrands
    allBrands = []
    allBrandsList = ''
    fatchedBrands = ''
    try:
        storeJson = json.loads(json.dumps(request.data))
    except Exception as e:
        context = {'Status': False, 'Message': 'Error Getting Brands Data..!'}
        ShowException(e)
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
        context = {'Status': False, 'Message': 'No Brands Data Found..!'}
        return Response(context)
    else:
        try:
            if re.search('all', storeJson['key'], re.I):
                endlimit = page * perPage
                startlimit = endlimit - perPage
                brandsList = Stores.objects.filter(nature__icontains='Brand')
                if brandsList:
                    brandslimit = brandsList[startlimit:endlimit]
                    allBrandsList = get_brands_info(brandslimit)
                    data = {"data": allBrandsList, "Status": True,
                            "Message": "All Brands ..!",
                            "totalBrands": len(brandsList),
                            "fatchedBrands": len(brandslimit),
                            "page": page}
                    return Response(data=data)
                else:
                    context = {'Status': False, 'Message': 'No Brands Found '}
                    return Response(context)

            elif re.search(r'^[A-Z]', storeJson['key'], re.I):
                endlimit = page * perPage
                startlimit = endlimit - perPage
                brandsList = Stores.objects.filter(nature__icontains='Brand', store_name__istartswith=storeJson['key'])
                if brandsList:
                    brandslimit = brandsList[startlimit:endlimit]
                    allBrandsList = get_brands_info(brandslimit)
                    data = {"data": allBrandsList, "Status": True,
                            "Message": "All Brands ..!",
                            "totalBrands": len(brandsList),
                            "fatchedBrands": len(brandslimit),
                            "page": page}
                    return Response(data=data)
                else:
                    context = {'Status': False, 'Message': 'No Brands Found with : ' + str(storeJson['key'])}
                    return Response(context)

            elif re.search('0-9', storeJson['key']):
                digitList = []
                # ======= Pagination =======#
                endlimit = page * perPage
                startlimit = endlimit - perPage
                # ===== End Pagination ====#
                ranges = str(storeJson.get('key')).split('-')
                start, end = int(ranges[0]), int(ranges[1])
                if start < end:
                    digitList.extend(range(start, end))
                    digitList.append(end)

                for digit in digitList:
                    brandsList = Stores.objects.filter(nature__icontains='Brand', store_name__startswith=str(digit))
                    if not brandsList:
                        continue
                    else:
                        allBrandsList = get_brands_info(brandsList)
                        fatchedBrands = allBrandsList[startlimit:endlimit]

                data = {"data": fatchedBrands, "Status": True,
                        "Message": "Brands That Start With Digit ..!",
                        "totalBrands": len(allBrandsList),
                        "fatchedBrands": len(fatchedBrands),
                        "page": page}
                return Response(data)
        except Exception as e:
            context = {'Status': False, 'Message': 'Error While Getting data'}
            ShowException(e)
            return Response(context)


def get_brands_info(storesList):
    for store in storesList:
        productCount = Products.objects.filter(store_id=store.id).count()
        data = {
            "id": store.id,
            "store_name": store.store_name,
            "store_logo": store.store_logo,
            "store_url": store.store_url,
            "nature": store.nature,
            "products_count": productCount
        }
        allBrands.append(data)
    return allBrands


def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
