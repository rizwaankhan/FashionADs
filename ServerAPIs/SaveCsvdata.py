import csv
import os
import sys

from rest_framework.decorators import api_view
from rest_framework.response import Response

from ServerAPIs.models import *


@api_view(['GET', 'POST'])
def csvReader(request):
    csvPath = ''
    csvFile = ''
    try:
        csvPath = str((os.path.dirname(os.path.abspath(__file__)))).split('\FashionAppAPI')[0]
        csvFile = open("FashionAPI/Sampledata.csv", "r")
    except:
        for root, dirs, files in os.walk(csvPath):
            for name in files:
                if name == "Sampledata.csv":
                    csvFile = open(str(root) + "\\Sampledata.csv", "r")
    csvreader = csv.reader(csvFile)
    # headerData = next(csvreader)
    gender = ''
    if csvreader:
        next(csvreader)
        for data in csvreader:
            filters = tuple(data)
            try:
                gender = parent_categories.objects.get(parent_category_name=filters[0])

                if our_filters.objects.filter(filter_name=filters[0], filter_type=filters[1],
                                              parent_category_name=gender.parent_category_name,
                                              DressType=filters[5]).exists():

                    our_filters.objects.filter(filter_name=filters[0]).update(filter_name=filters[0],
                                                                              filter_type=filters[1],
                                                                              parent_category_id=gender.id,
                                                                              parent_category_name=gender.parent_category_name,
                                                                              parent_category_slug=gender.parent_category_slug,
                                                                              filter_attribute=filters[3],
                                                                              keywords=filters[4],
                                                                              DressType=filters[5],
                                                                              )

                    print('Filter Update')

                else:
                    our_filters.objects.create(filter_name=filters[0], filter_type=filters[1],
                                               parent_category_id=gender.id,
                                               parent_category_name=gender.parent_category_name,
                                               parent_category_slug=gender.parent_category_slug,
                                               filter_attribute=filters[3],
                                               keywords=filters[4],
                                               DressType=filters[5],
                                               ).save()
                    print('Filter Saved')
            except Exception as e:
                print(e)
    return Response(data="OK", status=200)


def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
