# Create your views here.
import ast
import datetime
import json
import os
import pathlib
import subprocess
import sys
import urllib.parse
from datetime import date, timedelta

import mysql.connector
from django.contrib import messages
# from django.db import connection
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader

from .models import Store, Currency, ScrapType, ScrapAlerts, FashionUser, ScrapError, ProductFilters


# connection = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="",
#     database="Scraper",
#     port=3306
# )
# cursor = connection.cursor()
# config = {
#     'user': 'root',
#     'password': '',
#     'host': 'localhost',
#     'port': '3306',
#     'database': 'Scraper',
#     'raise_on_warnings': True, }
#
# connection = mysql.connector.connect(**config)
# cursor = connection.cursor()


def Login_Admin(request):
    try:
        request.session['displayname'] = 'Admin'
        request.session['displayname']
        return HttpResponseRedirect('/admin_site/admin_index/')
    except:
        template = loader.get_template("login_admin.html")
        context = {
            "session": request.session,
        }
        return HttpResponse(template.render(context, request))


def Logout(request):
    try:
        # del request.session['displayname']
        return HttpResponseRedirect('/admin_site/login_admin/')
    except:
        return HttpResponseRedirect('/admin_site/login_admin/')


def Authenticate(request):
    if (request.method == 'POST'):
        try:
            email = request.POST.get('username', "")
            password = request.POST.get('password', "")
            if FashionUser.objects.filter(Email=email, Password=password).exists():
                displayname = FashionUser.objects.get(Email=email, Password=password).DisplayName
                request.session['displayname'] = displayname
                return HttpResponseRedirect('/admin_site/admin_index/')
            else:
                Info = 'Wrong Credentials. Please try again.'
                template = loader.get_template("login_admin.html")
                context = {
                    "session": request.session,
                    "email": email,
                    "password": password,
                    "Info": Info,
                }
                return HttpResponse(template.render(context, request))
        except:
            Info = 'There seems some problems in performing your operations. Please try again.'
            context = {
                "session": request.session,
                "Info": Info,
            }
            template = loader.get_template("login_admin.html")
            return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/admin_site/login_admin/')


def Index(request):
    try:
        request.session['displayname']
    except:
        return HttpResponseRedirect('/admin_site/login_admin/')
    template = loader.get_template("index_admin.html")
    context = {
        "session": request.session,
    }
    return HttpResponse(template.render(context, request))


def GetProductResultsAjax(request):
    print('in ajax')
    request.session['send_ajax'] = 'False'
    filepath = str(
        pathlib.Path(__file__).resolve().parent) + '\\Scrapers\\Scrapers\\spiders\\' + 'ProductFileTemp.json'
    data = []
    msg = 'False'
    out_of_stock = ''
    try:
        with open(filepath) as fp:
            data = json.load(fp)
            print(data)
            if data['Error_Flag'] == 'True':
                data = ([data['Error_in'], data['Error_msg'], data['Error_class'], data['Error_taceback'][0],
                         data['Error_taceback'][1], data['Error_taceback'][2], data['Error_url']])
                msg = 'Error'
            elif data['Error_Flag'] == 'Out of stock.':
                out_of_stock = data['out_of_stock']
                msg = 'Out of stock.'
                data = (['', '', '', '', '', '', data['Error_url']])
            else:
                data = (data['Results'])
                msg = 'True'
    except Exception as e:
        print(e)
        pass
    try:
        if msg == 'Error' or msg == 'True':
            path = pathlib.Path(filepath)
            path.unlink()
    except Exception as e:
        msg = 'Stop Function'
        pass
    context = {
        "msg": msg,
        "data": data,
        "out_of_stock": out_of_stock,
        "session": request.session,
    }
    return HttpResponse(json.dumps(context, indent=4, sort_keys=True, default=str))


def GetProductFilterAjax(request):
    print('in ajax filter')
    url = request.POST.get('url')
    print('url', url)
    try:
        filter_data = ProductFilters.objects.filter(ProductUrl=url)[0]
        data = [filter_data.Id, filter_data.ProductUrl, filter_data.DressStyle, filter_data.DressLength,
                filter_data.Occasion, filter_data.SleeveType, filter_data.SleeveLength, filter_data.Neckline,
                filter_data.Material, filter_data.Pattern, filter_data.Embellishment, filter_data.Character,
                filter_data.Feature, filter_data.FitType, filter_data.Closure, filter_data.GarmentCare,
                filter_data.Season, filter_data.Themes, filter_data.ShowOnly, filter_data.DateCreated,
                filter_data.DateUpdated,
                filter_data.FasteningType, filter_data.CuffStyle, filter_data.Collar
                ]
    except Exception as e:
        print(e)
        data = []
    print(data)
    context = {
        "data": data,
        "session": request.session,
    }
    return HttpResponse(json.dumps(context, indent=4, sort_keys=True, default=str))


def Scrap(request):
    global link
    try:
        request.session['displayname']
    except:
        return HttpResponseRedirect('/admin_site/login_admin/')
    try:
        token = request.GET.get('countryCode', ' ')
        if request.method == "POST":
            print('start scrapy')
            request.session['send_ajax'] = 'False'
            filename = ''
            classname = ''
            scraper_name = ''
            store_url = ''
            ScrapeNewUrl = request.POST.get('ScrapeNewUrl', 'false')

            ScrapeExistingUrlAgeInHour = request.POST.get('ScrapeExistingUrlAgeInHour', '0')
            ScrapeExistingUrlPriceDroppedInDay = request.POST.get('ScrapeExistingUrlPriceDroppedInDay', '')
            ScraperThreadCount = request.POST.get('ScraperThreadCount', '30')
            SendScrapeResultSummary = request.POST.get('SendScrapeResultSummary', 'true')
            DeleteProductAgeInDay = request.POST.get('DeleteProductAgeInDay', '')
            UploadProductPhoto = request.POST.get('UploadProductPhoto', 'false')
            CheckNewsletterProductAvailabilityAndWatermarkPhoto = request.POST.get(
                'CheckNewsletterProductAvailabilityAndWatermarkPhoto', 'false')
            UploadNewsletterPhoto = request.POST.get('UploadNewsletterPhoto', 'false')
            UploadOfferImage = request.POST.get('UploadOfferImage', 'false')
            SyncUserActivity = request.POST.get('SyncUserActivity', 'false')
            Reindex = request.POST.get('Reindex', 'false')
            UploadIndex = request.POST.get('UploadIndex', 'false')
            DeleteOldIndex = request.POST.get('DeleteOldIndex', 'false')
            DeleteOldPhoto = request.POST.get('DeleteOldPhoto', 'false')
            NotifyTodaysSale = request.POST.get('NotifyTodaysSale', 'false')
            CheckStoreForScrapeAlert = request.POST.get('CheckStoreForScrapeAlert', 'false')
            SendPriceAlert = request.POST.get('SendPriceAlert', 'false')
            SendSaleAlert = request.POST.get('SendSaleAlert', 'false')
            token = request.POST.get('token_name', '')
            link = request.POST.get('ProductUrl', '')
            storeIds = request.POST.getlist('storeId', '')
            pathfile = str(pathlib.Path().resolve()) + '\\FashionStores\\Scrapers\Scrapers\\spiders\\run.py '
            if storeIds:
                print('storeIds', storeIds)
                for store_ids in storeIds:
                    print('store_ids', store_ids)
                    StoreObj = Store.objects.get(Id=store_ids)
                    classname = StoreObj.ScrapperClassName
                    filename = classname.lower()
                    print(classname)
                    print(filename)
                    scraper_name = StoreObj.Name.replace(" ", "").replace('&', 'and')
                    print('scraper_name :', scraper_name)
                    store_url = StoreObj.Url
                    link = 'None'
                    if store_url[-1] != '/':
                        store_url = store_url + '/'
                    subprocess.Popen(
                        ["cmd", "/k", "python " + pathfile + filename, classname, scraper_name, store_url,
                         str(store_ids), link, ScrapeNewUrl],
                        shell=True)
                    messages.success(request, 'Scrapper Started Successfully!', extra_tags='alert-success fa-smile-o')

            elif link and ("https:" in link or "http:" in link):
                request.session['send_ajax'] = 'True'
                print('sending request true', request.session['send_ajax'])

                sub_pro_url = link.split('/')
                print("sub_pro_url:", sub_pro_url)

                product_url = sub_pro_url[0] + "//" + sub_pro_url[2]
                print("product_url:", product_url)

                StoreObj = Store.objects.get(Url__contains=product_url)
                classname = StoreObj.ScrapperClassName
                filename = classname.lower()
                scraper_name = StoreObj.Name.replace(" ", "").replace('&', 'and')
                store_url = 'None'
                store_ids = StoreObj.Id
                link = urllib.parse.quote_plus(link)
                subprocess.Popen(
                    ["cmd", "/k", "python " + pathfile + filename, classname, scraper_name, store_url, str(store_ids),
                     link, "false"],
                    shell=True)
                messages.success(request,
                                 'Scrapper Started Successfully, Please wait. Scrapper is fetching results it will be displayed here shortly.',
                                 extra_tags='alert-success fa-smile-o')
            return HttpResponseRedirect('/admin_site/scrape/?countryCode=' + str(token))
        else:
            if token:
                Title = 'Scrape ' + str(token)
                template = loader.get_template("scrap.html")
                data = []
                for r in Currency.objects.all():
                    data.append([r.StoreId.Id, r.StoreId.Name, r.Code])
                context = {
                    "session": request.session,
                    "Title": Title,
                    "token": token,
                    "data": data,
                }
                return HttpResponse(template.render(context, request))
            else:
                return HttpResponseRedirect('/admin_site/admin_index/')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
        return HttpResponseRedirect('/admin_site/admin_index/')


def ScrapResults(request):
    try:
        request.session['displayname']
    except:
        return HttpResponseRedirect('/admin_site/login_admin/')
    try:
        total_errors = 0
        DateUpdated = ''
        DateUpdated_post = request.POST.get('DateUpdated', '')
        storeId = request.POST.get('storeId')
        if not storeId:
            storeId = request.GET.get('storeId')
            DateUpdated = request.GET.get('DateUpdated')
        try:
            store_id = int(storeId)
        except:
            store_id = ''
        product_data = []
        if storeId:
            config = {
                'user': 'root',
                'password': '',
                'host': 'localhost',
                'port': '3306',
                'database': 'Scraper',
                'raise_on_warnings': True, }

            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()
            if DateUpdated == 'today':
                date_query = " AND scrapresult.DateCreated >= '" + str(
                    datetime.datetime.now().date()) + " 00:00:00' AND scrapresult.DateCreated <= '" + str(
                    datetime.datetime.now().date()) + " 23:59:59'"

            elif DateUpdated == 'yesterday':
                yesterday = date.today() - timedelta(days=1)
                yesterday = yesterday.strftime('%Y-%m-%d')
                date_query = " And scrapresult.DateCreated >= '" + str(
                    yesterday) + " 00:00:00' AND scrapresult.DateCreated <= '" + str(
                    yesterday) + " 23:59:59'"
            elif DateUpdated_post:
                date_query = " And scrapresult.DateCreated >= '" + str(
                    DateUpdated_post) + " 00:00:00' AND scrapresult.DateCreated <= '" + str(
                    DateUpdated_post) + " 23:59:59'"
            else:
                date_query = ''
                DateUpdated_post = ''
            cursor.execute(
                """ SELECT ScrapResult.StoreId, Store.Name, ScrapResult.StartDateTime,ScrapResult.EndDateTime,ScrapResult.NewProductUrlCount,
                ScrapResult.ExistingProductUrlCount,ScrapResult.TotalDistinctProductUrlCount,ScrapResult.ProductAddedCount,ScrapResult.ProductUpdatedCount,
                ScrapResult.ProductDeletedCount,ScrapResult.ProductMergedCount,ScrapResult.SaleProductCount,ScrapResult.TotalProductCount,
                 ScrapResult.ProductWithProductSizeCount,ScrapResult.ProductSizeAvailableCount,ScrapResult.ProductSizeWithColorCount,
                 ScrapResult.TotalProductSizeCount,ScrapResult.ProductWithBrandCount,ScrapResult.UniqueBrandCount,ScrapResult.WarningCount,ScrapResult.ErrorCount,
                 ScrapResult.Id FROM `ScrapResult` INNER JOIN Store ON Store.Id=ScrapResult.StoreId WHERE StoreId=""" + str(
                    storeId) + date_query + """ ORDER BY ScrapResult.Id DESC """)
            for r in (cursor.fetchall()):
                duration = r[3] - r[2]
                duration_in_s = duration.total_seconds()
                timetaken = str(divmod(duration_in_s, 3600)[0]) + ' hours'
                if ScrapError.objects.filter(ScrapResultId=r[21]).exists() == True:
                    Error_Count = ScrapError.objects.filter(ScrapResultId=r[21])
                    for row in Error_Count:
                        total_errors += row.Count
                    Error_Id = r[21]
                    Error_msg = '\n See ' + str(Error_Count.count()) + ' Error'
                else:
                    Error_Id = 'False'
                    Error_msg = ''
                try:
                    sales_percentage = round((r[11] / r[6]) * 100) if r[6] > 0 else round((r[11] / r[
                        4]) * 100)  # Sale Product Count & Percent/Total Distinct Product Url Count or New Product Url Count
                except:
                    sales_percentage = 0
                try:
                    Product_with_Size_Count_Percent = round(
                        (r[13] / r[12]) * 100)  # Product with Size Count & Percent/Total Product Count
                except:
                    Product_with_Size_Count_Percent = 0
                try:
                    Product_Size_Available_Count_Percent = round(
                        (r[14] / r[16]) * 100)  # Product with Size Count & Percent/Total Product Size Count
                except:
                    Product_Size_Available_Count_Percent = 0
                try:
                    Product_Size_with_Colour_Count_Percent = round(
                        (r[15] / r[16]) * 100)  # Product Size with Colour Count & Percent/Total Product Size Count
                except:
                    Product_Size_with_Colour_Count_Percent = 0
                try:
                    Product_With_Brand_CountPercent = round(
                        (r[17] / r[12]) * 100)  # Product_With_Brand_CountPercent/Total Product Size Count
                except:
                    Product_With_Brand_CountPercent = 0
                try:
                    Warning_Count_Percent = round((r[19] / r[12]) * 100)  # ????????????
                except:
                    Warning_Count_Percent = 0
                try:
                    Error_Count_Percent = round((r[20] / r[6]) * 100) if r[6] > 0 else round((r[20] / r[
                        4]) * 100)  # Error Count & Percent/Total Distinct Product Url Count or New Product Url Count
                except:
                    Error_Count_Percent = 0
                product_data.append(
                    [r[0], r[1], r[2], r[3], timetaken, r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13]
                        , r[14], r[15], r[16], r[17], r[18], r[19], r[20], Error_Id, Error_msg, total_errors,
                     '\n' + str(sales_percentage), '\n' + str(Product_with_Size_Count_Percent),
                     '\n' + str(Product_Size_Available_Count_Percent),
                     '\n' + str(Product_Size_with_Colour_Count_Percent), '\n' + str(Product_With_Brand_CountPercent),
                     '\n' + str(Warning_Count_Percent), '\n' + str(Error_Count_Percent)
                     ])
            cursor.close()

        data = []
        for r in Currency.objects.all():
            data.append([r.StoreId.Id, r.StoreId.Name, r.Code])
        template = loader.get_template("scrap_result.html")
        context = {
            "session": request.session,
            "data": data,
            "DateUpdated_post": DateUpdated_post,
            "product_data": product_data,
            "storeId": store_id,
        }

        return HttpResponse(template.render(context, request))
    except Exception as e:
        print(e)
        return HttpResponseRedirect('/admin_site/admin_index/')


def ScrapResultsError(request):
    try:
        request.session['displayname']
    except:
        return HttpResponseRedirect('/admin_site/login_admin/')
    try:
        ScrapResultId = request.GET.get('ScrapResultId')
        product_data = []
        error_details = []
        total_errors = 0
        config = {
            'user': 'root',
            'password': '',
            'host': 'localhost',
            'port': '3306',
            'database': 'Scraper',
            'raise_on_warnings': True, }

        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute(
            """ SELECT ScrapResult.StoreId, Store.Name, ScrapResult.StartDateTime,ScrapResult.EndDateTime,ScrapResult.NewProductUrlCount,
            ScrapResult.ExistingProductUrlCount,ScrapResult.TotalDistinctProductUrlCount,ScrapResult.ProductAddedCount,ScrapResult.ProductUpdatedCount,
            ScrapResult.ProductDeletedCount,ScrapResult.ProductMergedCount,ScrapResult.SaleProductCount,ScrapResult.TotalProductCount,
             ScrapResult.ProductWithProductSizeCount,ScrapResult.ProductSizeAvailableCount,ScrapResult.ProductSizeWithColorCount,
             ScrapResult.TotalProductSizeCount,ScrapResult.ProductWithBrandCount,ScrapResult.UniqueBrandCount,ScrapResult.WarningCount,ScrapResult.ErrorCount,
             ScrapResult.Id FROM `ScrapResult` INNER JOIN Store ON Store.Id=ScrapResult.StoreId WHERE ScrapResult.Id=""" + str(
                ScrapResultId) + """  """)
        for r in (cursor.fetchall()):
            duration = r[3] - r[2]
            duration_in_s = duration.total_seconds()
            timetaken = str(divmod(duration_in_s, 3600)[0]) + ' hours'
            error_details = []
            if ScrapError.objects.filter(ScrapResultId=r[21]).exists() == True:
                Error_Count = ScrapError.objects.filter(ScrapResultId=r[21])
                total_errors = 0
                for row in Error_Count:
                    UrlList = json.loads(row.UrlList)
                    StackTrace = json.loads(row.StackTrace)
                    total_errors += row.Count
                    error_details.append(
                        [row.Id, row.ScrapResultId, row.Message, StackTrace, UrlList, row.Count, row.Exception,
                         row.DateCreated])
                Error_Id = r[21]
                Error_msg = '\n See ' + str(Error_Count.count()) + ' Error'
            else:
                Error_Id = 'False'
                Error_msg = ''
            product_data.append([r[0], r[1], r[2], r[3], timetaken, r[4], r[5], r[6],
                                 r[7], r[8], r[9], r[10], r[11], r[12], r[13]
                                    , r[14], r[15], r[16], r[17], r[18], r[19], r[20], Error_Id, Error_msg])
        cursor.close()
        template = loader.get_template("scrap_result_error.html")
        context = {
            "session": request.session,
            "product_data": product_data,
            "error_details": error_details,
            "total_errors": total_errors,
        }
        return HttpResponse(template.render(context, request))
    except Exception as e:
        print(e)
        return HttpResponseRedirect('/admin_site/admin_index/')


def Brand_list(request):
    try:
        request.session['displayname']
    except:
        return HttpResponseRedirect('/admin_site/login_admin/')
    try:
        storeId = request.GET.get('storeId')
        ShowSimilarBrand = request.GET.get('ShowSimilarBrand')
        try:
            store_id = int(storeId)
        except:
            store_id = ''
        brand_data = []
        no_brand_data = []
        if storeId:
            config = {
                'user': 'root',
                'password': '',
                'host': 'localhost',
                'port': '3306',
                'database': 'Scraper',
                'raise_on_warnings': True, }

            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()
            cursor.execute(
                """ SELECT Brand,count(Id) as total,Url FROM `product` WHERE StoreId=""" + str(
                    storeId) + """ and Brand!='' GROUP BY Brand """)
            for r in (cursor.fetchall()):
                brand_data.append([r[0], r[1], r[2]])
            cursor.execute(
                """ SELECT Name,Url FROM `product` WHERE StoreId=""" + str(
                    storeId) + """ and Brand='' """)
            for r in (cursor.fetchall()):
                no_brand_data.append([r[0], r[1]])
            cursor.close()
        data = []
        for r in Currency.objects.all():
            data.append([r.StoreId.Id, r.StoreId.Name, r.Code])
        template = loader.get_template("brand_list.html")
        if ShowSimilarBrand == "True":
            template = loader.get_template("brand_list_similar.html")
        context = {
            "session": request.session,
            "data": data,
            "storeId": store_id,
            "brand_data": brand_data,
            "no_brand_data": no_brand_data,
            "len_brand_data": len(brand_data),
            "len_no_brand_data": len(no_brand_data),
        }
        return HttpResponse(template.render(context, request))
    except Exception as e:
        print(e)
        return HttpResponseRedirect('/admin_site/admin_index/')


def Product_List(request):
    try:
        request.session['displayname']
    except:
        return HttpResponseRedirect('/admin_site/login_admin/')
    try:
        DateUpdated = ''
        DateUpdated_post = request.POST.get('DateUpdated', '')
        Deleted = request.POST.get('Deleted', '0')
        storeId = request.POST.get('storeId')
        if not storeId:
            storeId = request.GET.get('storeId')
            DateUpdated = request.GET.get('DateUpdated', '')
        try:
            store_id = int(storeId)
        except:
            store_id = ''
        product_data = []
        if storeId:
            config = {
                'user': 'root',
                'password': '',
                'host': 'localhost',
                'port': '3306',
                'database': 'Scraper',
                'raise_on_warnings': True, }

            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()
            if DateUpdated == 'today':
                date_query = " AND DateUpdated >= '" + str(
                    datetime.datetime.now().date()) + " 00:00:00' AND DateUpdated <= '" + str(
                    datetime.datetime.now().date()) + " 23:59:59'"
            elif DateUpdated == 'yesterday':
                yesterday = date.today() - timedelta(days=1)
                yesterday = yesterday.strftime('%Y-%m-%d')
                date_query = " And DateUpdated >= '" + str(yesterday) + " 00:00:00' AND DateUpdated <= '" + str(
                    yesterday) + " 23:59:59'"
            elif DateUpdated_post:
                date_query = " And DateUpdated >= '" + str(DateUpdated_post) + " 00:00:00' AND DateUpdated <= '" + str(
                    DateUpdated_post) + " 23:59:59'"
            else:
                date_query = ''
                DateUpdated_post = ''

            cursor.execute(
                """ SELECT Name,Url,Brand,Price,SalePrice,DateCreated,DateUpdated,ImageUrl FROM `product` WHERE StoreId="""
                + str(storeId) + date_query + """ AND Deleted=""" + str(Deleted) + """ """)
            for idx, r in enumerate(cursor.fetchall()):
                try:
                    img_urls = ast.literal_eval(r[7])
                except Exception as e:
                    img_urls = [r[7]]

                product_data.append([r[0], r[1], r[2], r[3], r[4], r[5], r[6], img_urls])
            cursor.close()
        template = loader.get_template("product_list.html")
        data = []
        for r in Currency.objects.all():
            data.append([r.StoreId.Id, r.StoreId.Name, r.Code])
        context = {
            "session": request.session,
            "product_data": product_data,
            "storeId": store_id,
            "data": data,
            "Deleted": Deleted,
            "DateUpdated": DateUpdated_post,
        }
        return HttpResponse(template.render(context, request))
    except Exception as e:
        print(e)
        return HttpResponseRedirect('/admin_site/admin_index/')


def Product_size(request):
    try:
        request.session['displayname']
    except:
        return HttpResponseRedirect('/admin_site/login_admin/')
    try:
        unique_sizes = []
        unavailable_sizes = []
        unique_colours = []
        without_sizes = []
        multiple_colors = []
        sizes_and_without_color = []
        storeId = request.GET.get('storeId')
        try:
            store_id = int(storeId)
        except:
            store_id = ''
        if storeId:
            config = {
                'user': 'root',
                'password': '',
                'host': 'localhost',
                'port': '3306',
                'database': 'Scraper',
                'raise_on_warnings': True, }

            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()
            cursor.execute(
                """ SELECT Size,COUNT(ProductId) as ProductCount, COUNT(Size) as ProductSizeCount ,Product.Url FROM `ProductSize` INNER JOIN Product ON ProductSize.ProductId=Product.Id WHERE Product.StoreId=""" + str(
                    storeId) + """ and Size!='' GROUP BY Size """)
            for r in (cursor.fetchall()):
                unique_sizes.append([r[0], r[1], r[2], r[3]])

            cursor.execute(
                """ SELECT Size,COUNT(ProductId) as ProductCount, COUNT(Size) as ProductSizeCount ,Url FROM `ProductSize` INNER JOIN Product ON ProductSize.ProductId=Product.Id WHERE Product.StoreId=""" + str(
                    storeId) + """ AND Size!='' AND Available=0 GROUP BY Size """)
            for r in (cursor.fetchall()):
                unavailable_sizes.append([r[0], r[1], r[2], r[3]])
            cursor.execute(
                """ SELECT Color,COUNT(ProductId) as ProductCount, COUNT(Size) as ProductSizeCount ,Url FROM `ProductSize` INNER JOIN Product ON ProductSize.ProductId=Product.Id WHERE Product.StoreId=""" + str(
                    storeId) + """ AND Size!='' GROUP BY Color """)
            for r in (cursor.fetchall()):
                unique_colours.append([r[0], r[1], r[2], r[3]])
            cursor.execute(
                """ SELECT Product.Name,Product.Url FROM `ProductSize` INNER JOIN Product ON ProductSize.ProductId=Product.Id WHERE Product.StoreId=""" + str(
                    storeId) + """ and Size='' """)
            for r in (cursor.fetchall()):
                without_sizes.append([r[0], r[1]])
            cursor.execute(
                """ SELECT Product.Name,Product.Url FROM `ProductSize` INNER JOIN Product ON ProductSize.ProductId=Product.Id WHERE Product.StoreId=""" + str(
                    storeId) + """ AND Size!='' AND Color=''""")
            for r in (cursor.fetchall()):
                sizes_and_without_color.append([r[0], r[1]])
            cursor.execute(
                """SELECT Product.Name,Product.Url, count(distinct Color) as multiple_colours ,ProductSize.Id FROM `ProductSize` INNER JOIN Product ON ProductSize.ProductId=Product.Id WHERE Product.StoreId=""" + str(
                    storeId) + """ GROUP by ProductSize.ProductId HAVING multiple_colours>1""")
            for r in (cursor.fetchall()):
                multiple_colors.append([r[0], r[1]])
            cursor.close()
        template = loader.get_template("product_size_list.html")
        data = []
        for r in Currency.objects.all():
            data.append([r.StoreId.Id, r.StoreId.Name, r.Code])
        context = {
            "session": request.session,
            "storeId": store_id,
            "unique_sizes": unique_sizes,
            "unique_sizes_len": len(unique_sizes),
            "unavailable_sizes": unavailable_sizes,
            "unavailable_sizes_len": len(unavailable_sizes),
            "unique_colours": unique_colours,
            "unique_colours_len": len(unique_colours),
            "without_sizes": without_sizes,
            "without_sizes_len": len(without_sizes),
            "sizes_and_without_color": sizes_and_without_color,
            "sizes_and_without_color_len": len(sizes_and_without_color),
            "multiple_colors": multiple_colors,
            "multiple_colors_len": len(multiple_colors),
            "data": data,
        }
        return HttpResponse(template.render(context, request))
    except Exception as e:
        print(e)
        return HttpResponseRedirect('/admin_site/admin_index/')


def Store_List(request):
    try:
        request.session['displayname']
    except:
        return HttpResponseRedirect('/admin_site/login_admin/')
    try:
        data = []
        config = {
            'user': 'root',
            'password': '',
            'host': 'localhost',
            'port': '3306',
            'database': 'Scraper',
            'raise_on_warnings': True, }

        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute(
            """ SELECT currency.Code,currency.Name,scraptype.Code,scraptype.Name,store.Id,store.Name,store.Description,store.Url,store.AffiliateUrl,store.AUSite,store.NZSite,store.USSite,store.ScrapperClassName,store.DownloadThreadCount,store.ScrapThreadCount,store.MergeProductSize,store.NoReferrer,store.Hidden,store.DateUpdated FROM `store` INNER JOIN scraptype ON scraptype.StoreId=store.Id INNER JOIN currency ON currency.StoreId=store.Id; """)
        for idx, r in enumerate(cursor.fetchall()):
            site = ''
            if int(r[9]) == 1:
                site += 'AU '
            if int(r[10]) == 1:
                site += 'NZ '
            if int(r[11]) == 1:
                site += 'US '
            options = ''
            if int(r[15]) == 1:
                options += 'MergeProductSize '
            if int(r[16]) == 1:
                options += 'NoReferrer '
            if int(r[17]) == 1:
                options += 'Hidden '
            data.append([r[4], r[5], r[6], r[7], r[8], r[1], site, r[12], r[3], r[13], r[14], options, r[18]])
        cursor.close()
        template = loader.get_template("store_list.html")
        context = {
            "session": request.session,
            'Data': data,
            'total_stores': len(data),
        }
        return HttpResponse(template.render(context, request))
    except Exception as e:
        print(e)
        return HttpResponseRedirect('/admin_site/admin_index/')


def Stores(request):
    try:
        request.session['displayname']
    except Exception as e:
        print(e)
        return HttpResponseRedirect('/admin_site/login_admin/')
    if request.method == "POST":
        try:
            Name = request.POST.get("Name")
            url = request.POST.get("url")
            AffiliateUrl = request.POST.get("AffiliateUrl")
            Description = request.POST.get("Description")
            CurrencyCode = request.POST.get("CurrencyCode")
            AUSite = request.POST.get("AUSite", 0)
            NZSite = request.POST.get("NZSite", 0)
            USSite = request.POST.get("USSite", 0)
            ScraperClassName = request.POST.get("ScraperClassName")
            ScrapeTypeCode = request.POST.get("ScrapeTypeCode")
            DownloadThreadCount = request.POST.get("DownloadThreadCount")
            ScrapeThreadCount = request.POST.get("ScrapeThreadCount")
            MergeProductSize = request.POST.get("MergeProductSize", 0)
            NoReferrer = request.POST.get("NoReferrer", 0)
            Hidden = request.POST.get("Hidden", 0)
            Store(Name=Name, Url=url, AffiliateUrl=AffiliateUrl, DownloadThreadCount=DownloadThreadCount,
                  DateCreated=datetime.datetime.now(), DateUpdated=datetime.datetime.now(),
                  Description=Description, MergeProductSize=MergeProductSize, ScrapThreadCount=ScrapeThreadCount,
                  AUSite=AUSite,
                  NZSite=NZSite, ScrapperClassName=ScraperClassName, USSite=USSite, NoReferrer=NoReferrer, Hidden=Hidden
                  ).save()
            Store_id = Store.objects.latest('Id')
            Currency(StoreId=Store_id, Code=CurrencyCode, Name=CurrencyCode).save()
            ScrapType(StoreId=Store_id, Code=ScrapeTypeCode, Name=ScrapeTypeCode).save()
            messages.success(request, 'Saved Successfully!', extra_tags='alert-success fa-smile-o')
            return HttpResponseRedirect('/admin_site/Store/')
        except Exception as e:
            print(e)
            messages.success(request,
                             'Hey, there seems some problems in performing your operations. Please try again later...!!!',
                             extra_tags='alert-danger fa-frown-o')
            return HttpResponseRedirect('/admin_site/Store/')
    else:
        try:
            template = loader.get_template("store.html")
            context = {
                "session": request.session,
            }
            return HttpResponse(template.render(context, request))
        except Exception as e:
            print(e)
            return HttpResponseRedirect('/admin_site/admin_index/')


def StoresUpdate(request):
    try:
        request.session['displayname']
    except:
        return HttpResponseRedirect('/admin_site/login_admin/')
    if request.method == "POST":
        try:
            store_id = request.POST.get("store_id")
            Name = request.POST.get("Name")
            url = request.POST.get("url")
            AffiliateUrl = request.POST.get("AffiliateUrl")
            Description = request.POST.get("Description")
            CurrencyCode = request.POST.get("CurrencyCode")
            AUSite = request.POST.get("AUSite", 0)
            NZSite = request.POST.get("NZSite", 0)
            USSite = request.POST.get("USSite", 0)
            ScraperClassName = request.POST.get("ScraperClassName", 0)
            ScrapeTypeCode = request.POST.get("ScrapeTypeCode", 0)
            DownloadThreadCount = request.POST.get("DownloadThreadCount", 0)
            ScrapeThreadCount = request.POST.get("ScrapeThreadCount", 0)
            MergeProductSize = request.POST.get("MergeProductSize", 0)
            NoReferrer = request.POST.get("NoReferrer", 0)
            Hidden = request.POST.get("Hidden", 0)
            Store.objects.filter(Id=store_id).update(Name=Name, Url=url, AffiliateUrl=AffiliateUrl,
                                                     DownloadThreadCount=DownloadThreadCount,
                                                     DateCreated=datetime.datetime.now(),
                                                     DateUpdated=datetime.datetime.now(),
                                                     Description=Description, MergeProductSize=MergeProductSize,
                                                     ScrapThreadCount=ScrapeThreadCount, AUSite=AUSite,
                                                     NZSite=NZSite, ScrapperClassName=ScraperClassName, USSite=USSite,
                                                     NoReferrer=NoReferrer, Hidden=Hidden
                                                     )
            Currency.objects.filter(Id=store_id).update(Code=CurrencyCode, Name=CurrencyCode)
            ScrapType.objects.filter(Id=store_id).update(Code=ScrapeTypeCode, Name=ScrapeTypeCode)
            messages.success(request, 'Updated Successfully!', extra_tags='alert-success fa-smile-o')
            return HttpResponseRedirect('/admin_site/StoreList/')
        except Exception as e:
            print(e)
            messages.success(request,
                             'Hey, there seems some problems in performing your operations. Please try again later...!!!',
                             extra_tags='alert-danger fa-frown-o')
            return HttpResponseRedirect('/admin_site/StoreList/')
    else:
        storeId = request.GET.get('storeId')
        try:
            if storeId:
                data = []
                config = {
                    'user': 'root',
                    'password': '',
                    'host': 'localhost',
                    'port': '3306',
                    'database': 'Scraper',
                    'raise_on_warnings': True, }

                connection = mysql.connector.connect(**config)
                cursor = connection.cursor()
                cursor.execute(
                    """ SELECT currency.Code,currency.Name,scraptype.Code,scraptype.Name,store.Id,store.Name,store.Description,store.Url,store.AffiliateUrl,store.AUSite,store.NZSite,store.USSite,store.ScrapperClassName,store.DownloadThreadCount,store.ScrapThreadCount,store.MergeProductSize,store.NoReferrer,store.Hidden,store.DateUpdated FROM `store` INNER JOIN scraptype ON scraptype.StoreId=store.Id INNER JOIN currency ON currency.StoreId=store.Id WHERE store.Id=""" + str(
                        storeId) + """; """)
                for idx, r in enumerate(cursor.fetchall()):
                    data.append(
                        [r[4], r[5], r[6], r[7], r[8], r[1], r[9], r[10], r[11], r[12], r[3], r[13], r[14], r[15],
                         r[16], r[17], r[18]])
                cursor.close()
                template = loader.get_template("store.html")
                context = {
                    "session": request.session,
                    "data": data[0],
                    "update": 'yes'
                }
                return HttpResponse(template.render(context, request))
            else:
                return HttpResponseRedirect('/admin_site/StoreList/')
        except Exception as e:
            print(e)
            return HttpResponseRedirect('/admin_site/admin_index/')


def Scrap_Alert(request):
    try:
        request.session['displayname']
    except:
        return HttpResponseRedirect('/admin_site/login_admin/')
    try:
        scrapAlertId = request.GET.get('scrapAlertId', ' ')
        if (request.method == 'POST'):
            try:
                scrapAlertIdIs = request.POST.get("scrapAlertIdIs", '')
                returnname = request.POST.get("returnname", '')
                Comment = request.POST.get("Comment", '')
                next_check = request.POST.get("next_check", '')
                Resolved = int(request.POST.get("Resolved", 0))
                ScrapAlerts.objects.filter(Id=scrapAlertIdIs).update(Resolved=Resolved, Comment=Comment,
                                                                     dayuntilnextcheck=next_check)
                messages.success(request, 'Updated Successfully!', extra_tags='alert-success fa-smile-o')
                if int(returnname) == int(1):
                    return HttpResponseRedirect('/admin_site/ScrapAlertList/')
                else:
                    return HttpResponseRedirect('/admin_site/ScrapAlert/?scrapAlertId=' + str(scrapAlertIdIs))
            except Exception as e:
                print(e)
                messages.success(request,
                                 'Hey, there seems some problems in performing your operations. Please try again later...!!!',
                                 extra_tags='alert-danger fa-frown-o')
        else:
            if not scrapAlertId:
                return HttpResponseRedirect('/admin_site/ScrapAlertList/')
            scraplist = []
            config = {
                'user': 'root',
                'password': '',
                'host': 'localhost',
                'port': '3306',
                'database': 'Scraper',
                'raise_on_warnings': True, }

            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()
            cursor.execute(
                """ SELECT store.Id,store.Name,scrapalerttype.Name,scrapalerts.Message,scrapalerts.Resolved,scrapalerts.Comment,scrapalerts.dayuntilnextcheck,scrapalerts.DateCreated,scrapalerts.DateUpdated ,scrapalerts.Id FROM scrapalerts INNER JOIN store ON store.Id=scrapalerts.StoreId INNER JOIN scrapalerttype ON scrapalerttype.Id=scrapalerts.ScrapAlertTypeId WHERE scrapalerts.Id=""" + str(
                    scrapAlertId) + """ ; """)
            for idx, r in enumerate(cursor.fetchall()):
                scraplist.append([r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]])
            cursor.close()
            template = loader.get_template("scrap_alert.html")
            context = {
                "session": request.session,
                "data": scraplist,
            }
            return HttpResponse(template.render(context, request))
    except Exception as e:
        print(e)
        return HttpResponseRedirect('/admin_site/admin_index/')


def ScrapAlert_List(request):
    try:
        request.session['displayname']
    except:
        return HttpResponseRedirect('/admin_site/login_admin/')
    try:
        data = []
        for r in Currency.objects.all():
            data.append([r.StoreId.Id, r.StoreId.Name, r.Code])
        config = {
            'user': 'root',
            'password': '',
            'host': 'localhost',
            'port': '3306',
            'database': 'Scraper',
            'raise_on_warnings': True, }
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        ResolvedTrue = request.GET.get('Resolved', 0)
        if ResolvedTrue == 'True':
            ResolvedTrue = 1
        Store_id = request.GET.get('storeId', 0)
        store_id = ''
        if Store_id != 0:
            store_id = ' AND store.Id=' + str(Store_id)
        scraplist = []
        cursor.execute(
            """ SELECT store.Id,store.Name,scrapalerttype.Name,scrapalerts.Message,scrapalerts.Resolved,scrapalerts.Comment,scrapalerts.dayuntilnextcheck,scrapalerts.DateCreated,scrapalerts.DateUpdated ,scrapalerts.Id FROM scrapalerts INNER JOIN store ON store.Id=scrapalerts.StoreId INNER JOIN scrapalerttype ON scrapalerttype.Id=scrapalerts.ScrapAlertTypeId WHERE scrapalerts.Resolved=""" + str(
                ResolvedTrue) + store_id + """ ; """)
        for idx, r in enumerate(cursor.fetchall()):
            resolved_value = "True"
            if r[4] == 0:
                resolved_value = 'False'

            scraplist.append([r[0], r[1], r[2], r[3], resolved_value, r[5], r[6], r[7], r[8], r[9]])
        cursor.close()
        template = loader.get_template("scrapalert_list.html")
        context = {
            "session": request.session,
            'data': data,
            'storeId': int(Store_id),
            'scraplist': scraplist,
            'scraplist_len': len(scraplist),
            'total_stores': len(data),
        }
        return HttpResponse(template.render(context, request))
    except Exception as e:
        print(e)
        return HttpResponseRedirect('/admin_site/admin_index/')
