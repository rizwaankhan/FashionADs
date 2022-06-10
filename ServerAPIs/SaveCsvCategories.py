import csv
import datetime
import os
import sys

from rest_framework.decorators import api_view
from rest_framework.response import Response

from ServerAPIs.models import *


@api_view(['GET', 'POST'])
def saveCsvCategory(request):
    csvPath = ''
    csvFile = ''
    try:
        csvPath = str((os.path.dirname(os.path.abspath(__file__)))).split('\FashionAppAPI')[0]
        csvFile = open("FashionAPI/categories.csv", "r")
    except:
        for root, dirs, files in os.walk(csvPath):
            for name in files:
                if name == "categories.csv":
                    csvFile = open(str(root) + "\\categories.csv", "r")
    csvreader = csv.reader(csvFile)
    # headerData = next(csvreader)
    if csvreader:
        next(csvreader)
        for data in csvreader:
            filters = tuple(data)
            try:
                gender = Parent_Categories.objects.get(parent_category_name=filters[0])
                if Our_Categories.objects.filter(category_name=filters[1],
                                                 parent_category_name=gender.parent_category_name).exists():
                    ourCatId = Our_Categories.objects.get(category_name=filters[1],
                                                          parent_category_name=gender.parent_category_name).id
                    Our_Categories.objects.filter(category_name=filters[1],
                                                  parent_category_name=gender.parent_category_name).update(
                        parent_category_id=gender.id,
                        parent_category_name=gender.parent_category_name
                        , category_name=filters[1],
                        keywords=filters[2],
                        category_slug=str(filters[1]).lower() + '-' + str(ourCatId),
                        products_count=Products.objects.filter(our_category_id=ourCatId).count(),
                        updated_at=datetime.datetime.now()
                    )
                    print('Filter Update')
                else:
                    ourCategoryInstance = Our_Categories.objects.create(parent_category_id=gender.id,
                                                                        parent_category_name=gender.parent_category_name
                                                                        , category_name=filters[1],
                                                                        keywords=filters[2],
                                                                        category_slug=str(filters[1]).lower()
                                                                        )
                    Our_Categories.objects.filter(id=ourCategoryInstance.id).update(
                        products_count=Products.objects.filter(our_category_id=ourCategoryInstance.id).count())
                    print('Filter Saved')
            except Exception as e:
                ShowException(e)
                return Response(data="error", status=400)
        return Response(data="OK", status=200)


def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
