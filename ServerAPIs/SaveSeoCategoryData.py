import json
import datetime
import traceback
from ServerAPIs.models import *
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['POST'])
def save_seo_category(request):
    try:
        categoryJson = json.loads(json.dumps(request.data))
    except Exception as e:
        ex = ShowException(e)
        context = {'Error': 'Error getting category data: ' + str(ex), 'return_data': []}
        return Response(context)

    hasDesc = True
    seoType = categoryJson.get('description')
    if seoType is None:
        seoType = categoryJson.get('keyword')
        hasDesc = False

    updated = 0
    failed = 0
    for value in seoType:
        try:
            categoryObj = Our_Categories.objects.get(parent_category_name__iexact=value[0],
                                                     category_name__iexact=value[1])
            if Our_Categories.objects.filter(parent_category_name__iexact=value[0],
                                             category_name__iexact=value[1]).exists():
                if hasDesc:
                    description = value[2]
                    seoKeywords = categoryObj.seo_keywords
                else:
                    seoKeywords = value[2]
                    description = categoryObj.description
                Our_Categories.objects.filter(parent_category_name__iexact=value[0],
                                              category_name__iexact=value[1]).update(
                    parent_category_id=categoryObj.parent_category_id,
                    parent_category_name=categoryObj.parent_category_name, category_name=categoryObj.category_name,
                    category_slug=categoryObj.category_slug, description=description, keywords=categoryObj.keywords,
                    seo_keywords=seoKeywords, products_count=categoryObj.products_count, parent_id=categoryObj.parent_id,
                    updated_at=datetime.datetime.now())
                updated += 1
        except Exception as e:
            failed += 1
            print(ShowException(e))
            continue
    context = {"flag": True, "total_updated": updated, "failed_to_update": failed}
    return Response(context)


def ShowException(e):
    return traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
