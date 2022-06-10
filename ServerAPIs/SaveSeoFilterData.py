import json
import datetime
import traceback
from ServerAPIs.models import *
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['POST'])
def save_seo_filter(request):
    try:
        filterJson = json.loads(json.dumps(request.data))
    except Exception as e:
        ex = ShowException(e)
        context = {'Error': 'Error getting filter data: ' + str(ex), 'return_data': []}
        return Response(context)

    hasDesc = True
    seoType = filterJson.get('description')
    if seoType is None:
        seoType = filterJson.get('keyword')
        hasDesc = False

    updated = 0
    failed = 0
    for value in seoType:
        try:
            parentCategory = value[0]
            if value[1] == 'garment_care' or value[1] == 'season':
                parentCategory = ''

            filterObj = Our_Filters.objects.get(parent_category_name__iexact=parentCategory, filter_type=value[1],
                                                filter_name__iexact=value[2])
            if Our_Filters.objects.filter(parent_category_name__iexact=parentCategory,
                                          filter_type=value[1], filter_name__iexact=value[2]).exists():
                if hasDesc:
                    description = value[3]
                    seoKeywords = filterObj.seo_keywords
                else:
                    seoKeywords = value[3]
                    description = filterObj.description
                Our_Filters.objects.filter(parent_category_name__iexact=parentCategory, filter_type=value[1],
                                           filter_name__iexact=value[2]).update(
                    parent_category_id=filterObj.parent_category_id,
                    parent_category_name=filterObj.parent_category_name, description=description,
                    parent_category_slug=filterObj.parent_category_slug, body_type=filterObj.body_type,
                    filter_type=filterObj.filter_type, filter_name=filterObj.filter_name, keywords=filterObj.keywords,
                    seo_keywords=seoKeywords, updated_at=datetime.datetime.now())
                updated += 1
        except Exception as e:
            failed += 1
            print(value[0], value[1], value[2])
            print(ShowException(e))
            continue
    context = {"flag": True, "total_updated": updated, "failed_to_update": failed}
    return Response(context)


def ShowException(e):
    return traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
