import json
import os
import re
import sys

import django
import requests
from rest_framework.response import Response

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FashionADs.settings")
django.setup()
from itertools import chain
from py_linq import Enumerable
from ServerAPIs.models import *


def SeoSearch():
    global searchedResults
    categoryFilters = list(
        Our_Categories.objects.values_list('parent_category_name', 'category_name', 'age', 'seo_keywords'))
    keyword_dict = {}
    try:
        for categoryFilter in categoryFilters:
            gender = categoryFilter[0]
            category = categoryFilter[1]
            filter_dict = {'parent_category_name': gender, 'our_category_name': category,
                           'our_category_name_2': category}
            seoKeywords = list(str(categoryFilter[3]).split(','))[:30]
            for seoKeyword in seoKeywords:
                remainingWord = re.sub(r'\s?(Dress(es)?)\s?', ' ',
                                       seoKeyword.title().replace(gender, '').replace(category, ''), re.I).rstrip()
                for word in remainingWord.split(' '):
                    nameMatched = Our_Filters.objects.filter(filter_name__icontains=word).values_list('filter_type',
                                                                                                         'filter_name')
                    keysMatched = Our_Filters.objects.filter(keywords__icontains=word).values_list('filter_type',
                                                                                                      'filter_name')
                    matched_data = list(chain(nameMatched, keysMatched))

                    if matched_data:
                        filter_types = list(set(Enumerable(matched_data).select(lambda x: x[0]).to_list()))
                        for filter_type in filter_types:
                            filter_dict[filter_type] = list(
                                set(Enumerable(matched_data).where(lambda x: x[0] == filter_type).select(
                                    lambda x: x[1]).to_list()))
                    else:
                        filter_dict['name'] = [word]

                context = {
                    "userid": 0,
                    "page": 0,
                    "products_per_page": "10",
                    "name-asc": False,
                    "name-desc": False,
                    "price-desc": False,
                    "price-asc": False
                }

                count = 0
                total_products = 0
                while total_products == 0 and count <= 1:
                    reqHeader = {'Content-Type': 'application/json'}
                    productUrl = 'https://e141-2407-aa80-314-c88f-64b7-e1b4-a5d3-396c.in.ngrok.io/api/' + 'GetProductsListing'
                    saveData = requests.post(url=productUrl, data=json.dumps(context | filter_dict), headers=reqHeader,
                                             timeout=6000)
                    print(context | filter_dict)
                    searchedResults = json.loads(saveData.text)
                    total_products = searchedResults["data"]["TotalProducts"]
                    if filter_dict.get('name') is not None:
                        del filter_dict['name']
                    count += 1

                if total_products > 0:
                    keyword_dict = {seoKeyword: filter_dict}

                print(keyword_dict)
    except Exception as e:
        context = {'data': {'Error': 'Error getting Searched Keywords', 'return_data': []}}
        ShowException(e)
        return Response(context)


def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)


if __name__ == '__main__':
    SeoSearch()
