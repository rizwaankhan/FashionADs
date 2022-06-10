import requests
from itertools import chain
from ServerAPIs.views import *


@api_view(['POST'])
@csrf_exempt
def search(request):
    global searchedResults
    filter_dict = {}
    searchJson = json.loads(json.dumps(request.data))
    try:
        if searchJson['query']:
            nameMatched = Our_Filters.objects.filter(filter_name__iexact=searchJson['query']).values_list(
                'filter_type', 'filter_name')
            keysMatched = Our_Filters.objects.filter(keywords__icontains=searchJson['query']).values_list('filter_type',
                                                                                                          'filter_name')
            matched_data = list(chain(nameMatched, keysMatched))

            filter_types = list(set(Enumerable(matched_data).select(lambda x: x[0]).to_list()))
            for filter_type in filter_types:
                filter_dict[filter_type] = list(
                    set(Enumerable(matched_data).where(lambda x: x[0] == filter_type).select(lambda x: x[1]).to_list()))

            print('dict_matched_data: ', filter_dict)
            context = {
                "userid": 0,
                "page": 0,
                "products_per_page": "10",
                "name-asc": False,
                "name-desc": False,
                "price-desc": False,
                "price-asc": False
            }

            if filter_dict:
                context = context | filter_dict
            else:
                filter_dict['name'] = [searchJson['query']]
                context = context | filter_dict
            reqHeader = {'Content-Type': 'application/json'}
            productUrl = 'http://localhost:8000/api/' + 'GetProductsListing'
            saveData = requests.post(url=productUrl, data=json.dumps(context), headers=reqHeader, timeout=6000,verify=False)
            searchedResults = json.loads(saveData.text)
    except Exception as e:
        context = {'data':
                       {'Error': 'Error getting Searched Keywords', 'return_data': []}
                   }
        ShowException(e)
        return Response(context)
    passed_to = {'passed_to': filter_dict}
    return Response(data=searchedResults | passed_to)

def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)