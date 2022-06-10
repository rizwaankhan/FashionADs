import csv
import datetime
import os
import sys

from rest_framework.decorators import api_view
from rest_framework.response import Response

from ServerAPIs.models import *


@api_view(['GET', 'POST'])
def csvReader(request):
    global status
    csvPath = ''
    csvFile = ''
    try:
        csvPath = str((os.path.dirname(os.path.abspath(__file__)))).split('\FashionAppAPI')[0]
        csvFile = open("FashionAPI/OurFilters.csv", "r")
    except:
        for root, dirs, files in os.walk(csvPath):
            for name in files:
                if name == "OurFilters.csv":
                    csvFile = open(str(root) + "\\OurFilters.csv", "r")
    csvreader = csv.reader(csvFile)
    # headerData = next(csvreader)
    gender = ''
    if csvreader:
        next(csvreader)
        for data in csvreader:
            filters = tuple(data)
            try:
                gender = Parent_Categories.objects.get(parent_category_name=filters[2])

                if Our_Filters.objects.filter(filter_name=filters[0], filter_type=filters[1],
                                              parent_category_name=gender.parent_category_name,
                                              DressType=filters[5]).exists():
                    Our_Filters.objects.filter(filter_name=filters[0]).update(filter_name=filters[0],
                                                                              filter_type=filters[1],
                                                                              parent_category_id=gender.id,
                                                                              parent_category_name=gender.parent_category_name,
                                                                              parent_category_slug=gender.parent_category_slug,
                                                                              filter_attribute=filters[3],
                                                                              keywords=filters[4],
                                                                              DressType=filters[5],
                                                                              updated_at=datetime.datetime.now()
                                                                              )

                    print('Filter Update')

                else:
                    Our_Filters.objects.create(filter_name=filters[0], filter_type=filters[1],
                                               parent_category_id=gender.id,
                                               parent_category_name=gender.parent_category_name,
                                               parent_category_slug=gender.parent_category_slug,
                                               filter_attribute=filters[3],
                                               keywords=filters[4],
                                               DressType=filters[5],

                                               ).save()
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