import traceback
from django.views.decorators.csrf import csrf_exempt
from ServerAPIs.models import *
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
@csrf_exempt
def fetch_all_filters(request):
    try:
        filterTypes = list(set(Our_Filters.objects.values_list('filter_type', flat=True)))
    except Exception as e:
        context = {'Error': 'Error getting filter types', 'return_data': []}
        ShowException(e)
        return Response(context)

    if not filterTypes:
        context = {'Error': 'Filters not found', 'return_data': []}
        return Response(context)

    filterDict = {}
    try:
        for filterType in filterTypes:
            filterDict[filterType] = list(
                Our_Filters.objects.filter(filter_type=filterType).values("id", "filter_name", "parent_category_id",
                                                                          "parent_category_name",
                                                                          "parent_category_slug",
                                                                          "keywords").distinct())
    except Exception as e:
        context = {'Error': 'Error getting filters data', 'return_data': []}
        ShowException(e)
        return Response(context)
    # print(our_filters.objects.values('filter_type').annotate(dcount=Count('filter_type')))
    return Response(filterDict)


def ShowException(e):
    return traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)