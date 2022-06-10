import datetime
import json
import operator
import os
import re
import sys
from collections import Counter
from functools import reduce

import pytz
# from django.db import connection
import mysql.connector
from django.db.models import Q, Avg
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from py_linq import Enumerable
from .models import *

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="Api",
    port=3306
)
cursor = connection.cursor()


# https://df3a-119-156-31-106.ngrok.io/GetProductsListing

def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)


def UpdateRating(business_id):
    rating_average = Business_Reviews.objects.filter(business_id=business_id).aggregate(Avg('rating'))['rating__avg']
    if not rating_average:
        rating_average = 0
    Businesses.objects.filter(id=business_id.id).update(rating=rating_average)
    return


def ConvertTimeToBusinessTimezone(datetime_object, time_zone):
    datetime_object = time_zone.localize(datetime_object)
    datetime_object = datetime_object.astimezone(time_zone)
    return datetime_object


def ConvertTimeFromBusinessToUserTimezone(time_object, time_zone):
    time_object = time_object.astimezone(time_zone)

    return time_object


def GetOpenClose(days_dictionry, time_zone, business_timezone_now, user_timezone_now, tz):
    is_open = False
    opening_today = False
    closing_today = False
    is_holiday = False
    timezone_day_name = business_timezone_now.strftime("%a")
    for keys in days_dictionry:
        if keys["title"] == timezone_day_name:
            if keys["duration"].lower() == 'closed':
                is_holiday = True
                is_open = False
                opening_today = 'Closed'
                closing_today = 'Closed'
            elif keys["duration"] == 'Open 24 Hours' or keys["duration"] == '24hr':
                is_holiday = False
                is_open = True
                opening_today = 'Open 24 Hours'
                closing_today = 'Open 24 Hours'

            else:

                try:
                    time_object1 = datetime.datetime.strptime(
                        str(user_timezone_now.date()) + " " + str(keys["duration"].split("-")[0].upper()),
                        '%Y-%m-%d %H:%M%p')
                    time_object2 = datetime.datetime.strptime(
                        str(user_timezone_now.date()) + " " + str(keys["duration"].split("-")[1].upper()),
                        '%Y-%m-%d %H:%M%p')
                except:
                    if keys["duration"][0:2] == '0:':
                        keys["duration"] = keys["duration"][2:]
                    time_object1 = datetime.datetime.strptime(
                        str(user_timezone_now.date()) + " " + str(keys["duration"].split("-")[0].upper()),
                        '%Y-%m-%d %H%p')
                    time_object2 = datetime.datetime.strptime(
                        str(user_timezone_now.date()) + " " + str(keys["duration"].split("-")[1].upper()),
                        '%Y-%m-%d %H%p')

                # Time With Businesses Timezone
                time_object1 = ConvertTimeToBusinessTimezone(time_object1, time_zone)
                time_object2 = ConvertTimeToBusinessTimezone(time_object2, time_zone)
                # Time With converting Businesses Timezone to User Timezone
                time_object1 = ConvertTimeFromBusinessToUserTimezone(time_object1, tz)
                time_object2 = ConvertTimeFromBusinessToUserTimezone(time_object2, tz)
                opening_today = time_object1.time().strftime("%I:%M %p")
                closing_today = time_object2.time().strftime("%I:%M %p")
                if time_object1.time() <= business_timezone_now.time() <= time_object2.time():
                    is_open = True
                    is_holiday = False
                else:
                    is_open = False
                    is_holiday = False
            break
    return is_open, is_holiday, opening_today, closing_today


def GetOpenCloseMain(opening_closing_change, opening_closing_hours_meta, time_zone, business_timezone_now,
                     user_timezone_now, tz):
    is_open, opening_today, closing_today, is_holiday = False, False, False, False
    if opening_closing_change:
        for open_close in opening_closing_change:
            for key, value in open_close.items():
                date_year = key.split(' to ')
                # Time With Businesses Timezone
                datetime_object1 = ConvertTimeToBusinessTimezone(datetime.datetime.strptime(
                    str(business_timezone_now.year) + '/' + date_year[0].strip() + " 00:00:00", '%Y/%m/%d %H:%M:%S'),
                    time_zone)
                datetime_object2 = ConvertTimeToBusinessTimezone(datetime.datetime.strptime(
                    str(business_timezone_now.year) + '/' + date_year[1].strip() + " 23:59:59", '%Y/%m/%d %H:%M:%S'),
                    time_zone)
                if datetime_object1 <= business_timezone_now <= datetime_object2:
                    is_open, is_holiday, opening_today, closing_today = GetOpenClose(value, time_zone,
                                                                                     business_timezone_now,
                                                                                     user_timezone_now, tz)
    elif opening_closing_hours_meta:
        try:
            json_list = json.loads(opening_closing_hours_meta)
            json.dumps(json_list)
            is_open, is_holiday, opening_today, closing_today = GetOpenClose(json_list, time_zone,
                                                                             business_timezone_now, user_timezone_now,
                                                                             tz)
        except:
            pass
    return is_open, is_holiday, opening_today, closing_today


@api_view(['POST'])
@csrf_exempt
def GetProductsListing(request):
    global shipping_label
    filter_type = ''
    filter_name = ''
    filter_gender = ''
    try:
        criterion1, criterion2, criterion3, criterion4, criterion5, criterion6, criterion7, criterion8, criterion9, criterion10 = Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q()
        criterion11, criterion12, criterion13, criterion14, criterion15, criterion16, criterion17, criterion18, criterion19, criterion20 = Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q()
        criterion21, criterion22, criterion23, criterion24, criterion25, criterion26, criterion27, criterion28, criterion29, criterion30 = Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q()
        criterion31, criterion32, criterion33, criterion34, criterion35, criterion36, criterion37, criterion38, criterion39, criterion40 = Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q()
        criterion41, criterion42, criterion43, criterion44, criterion45 = Q(), Q(), Q(), Q(), Q()

        input_data = request.data
        try:
            if len(input_data) == 0:
                error = "Error in getting data, request body is empty."
                context = {'Message': error, 'return_data': []}
                return Response(context)
        except:
            error = "Error in getting data, request body is empty."
            context = {'Message': error, 'return_data': []}
            return Response(context)
        try:
            page = int(input_data['page'])
            page = 1 if page == 0 else page
        except:
            page = 1
        try:
            products_per_page = int(input_data['products_per_page'])
        except:
            products_per_page = 40
        try:
            name_asc = (input_data['name-asc'])
        except:
            name_asc = ''
        try:
            name_desc = (input_data['name-desc'])
        except:
            name_desc = ''
        try:
            price_asc = (input_data['price-asc'])
        except:
            price_asc = ''
        try:
            price_desc = (input_data['price-desc'])
        except:
            price_desc = ''
        name_asc = '-name' if name_desc == True else 'name'
        price_asc, sale_price_asc = ('-sale_price', '-price') if price_desc == True else ('sale_price', 'price')

        try:
            sort = (input_data['sort'])
            page = 1 if sort == True else page
        except:
            pass

        try:
            query = ''
            url_query = str(input_data['website_url'])
            url_query = '' if url_query == "False" or url_query == '0' or url_query == '' else url_query
            url_query = re.sub(r'page=\d+((\?|&)?)', '', url_query).rstrip('?').rstrip('&')
            print(url_query)

            if not 'shop' in url_query:
                if "&" in url_query:
                    query = url_query.split('&')[-1]
                elif "?" in url_query:
                    query = url_query.split('?')[1]

                if query == '':
                    genderList = ['women', 'men', 'girls', 'boys', 'baby girls', 'baby boys']
                    filter_gender = Enumerable(genderList).where(lambda x: x in url_query).first_or_default()
                    home_nav = url_query.split('http://localhost:4200/')[1].split('/')
                    if not filter_gender and len(home_nav) == 1:
                        filter_type = 'offer_type'
                        filter_name = home_nav[0]
                    elif len(home_nav) == 2:
                        filter_name = home_nav[1]
                    elif len(home_nav) == 3:
                        filter_name = home_nav[2]
                else:
                    filter_type = query.split('=')[0]
                    filter_name = query.split('=')[1]

                if filter_type == '':
                    filter_data = list(Our_Filters.objects.filter(parent_category_name__iexact=filter_gender,
                                                                  filter_name__iexact=filter_name).values_list(
                        'filter_type',
                        'filter_name'))
                    if not filter_data:
                        filter_data = list(
                            Our_Filters.objects.filter(filter_name__iexact=filter_name).values_list('filter_type',
                                                                                                    'filter_name'))
                        filter_gender = ''
                    filter_type = filter_data[0][0]
                    filter_name = filter_data[0][1]
        except Exception as e:
            ShowException(e)

        print('gender:', filter_gender)
        print('filter_type: ', filter_type)
        print('filter_name: ', filter_name)

        try:
            store_id = (input_data['store_id'])
            store_id = '' if (store_id == "False" or (store_id) == '0' or store_id == '') else store_id
            if store_id and type(store_id) == int:
                criterion1 = Q(store_id=store_id)
            elif store_id and type(store_id) == str:
                criterion1 = Q(store_name__iexact=store_id)
            elif store_id and type(store_id) == list:
                criterion1 = Q(
                    reduce(operator.or_, (Q(store_name__iexact=x) for x in store_id))) if store_id else Q()
            else:
                Q()
        except Exception as e:
            ShowException(e)

        try:
            brand_id = (input_data['brand_id'])
            brand_id = [] if (brand_id == False or brand_id == 0 or brand_id == '') else brand_id
            if brand_id and type(brand_id[0]) == int:
                criterion2 = Q(reduce(operator.or_, (Q(brand_id=x) for x in brand_id)))
            elif brand_id and type(brand_id[0]) == str:
                criterion2 = Q(reduce(operator.or_, (Q(brand__iexact=x) for x in brand_id)))
            elif brand_id and type(brand_id) == list:
                criterion2 = Q(reduce(operator.or_, (Q(brand__iexact=x) for x in brand_id))) if brand_id and type(
                    brand_id[0]) == str else Q()
            else:
                Q()
        except Exception as e:
            ShowException(e)

        try:
            promo_offer_type = (input_data['promo_offer_type'])
            promo_offer_type = [] if promo_offer_type == False or promo_offer_type == 0 or promo_offer_type == '' else promo_offer_type
            criterion3 = Q(
                reduce(operator.or_,
                       (Q(promo_offer_type__icontains=x) for x in promo_offer_type))) if promo_offer_type else Q()
        except Exception as e:
            ShowException(e)
        try:
            price_offer_type = (input_data['price_offer_type'])
            price_offer_type = [] if price_offer_type == False or price_offer_type == 0 or price_offer_type == '' else price_offer_type
            criterion6 = Q(
                reduce(operator.or_,
                       (Q(price_offer_type__icontains=x) for x in price_offer_type))) if price_offer_type else Q()
        except Exception as e:
            ShowException(e)
        try:
            shipping_offer_type = (input_data['shipping_offer_type'])
            print(shipping_offer_type)
            shipping_offer_type = [] if shipping_offer_type == False or shipping_offer_type == 0 or shipping_offer_type == '' else shipping_offer_type
            criterion4 = Q(
                reduce(operator.or_,
                       (Q(shipping_offer_type__icontains=x) for x in
                        shipping_offer_type))) if shipping_offer_type else Q()
            print(criterion4)
        except Exception as e:
            ShowException(e)
        try:
            other_offer_type = (input_data['other_offer_type'])
            other_offer_type = [] if other_offer_type == False or other_offer_type == 0 or other_offer_type == '' else other_offer_type
            criterion5 = Q(
                reduce(operator.or_,
                       (Q(other_offer_type__icontains=x) for x in other_offer_type))) if other_offer_type else Q()
        except Exception as e:
            ShowException(e)

        try:
            authenticity_guarantee = str(input_data['authenticity_guarantee'])
            authenticity_guarantee = '' if authenticity_guarantee == "False" or authenticity_guarantee == '0' or authenticity_guarantee == '' else authenticity_guarantee
            criterion6 = Q(authenticity_guarantee=authenticity_guarantee) if authenticity_guarantee else Q()
        except Exception as e:
            ShowException(e)
        try:
            climate_pledge_friendly = str(input_data['climate_pledge_friendly'])
            climate_pledge_friendly = '' if climate_pledge_friendly == "False" or climate_pledge_friendly == '0' or climate_pledge_friendly == '' else climate_pledge_friendly
            criterion7 = Q(climate_pledge_friendly=climate_pledge_friendly) if climate_pledge_friendly else Q()
        except Exception as e:
            ShowException(e)
        try:
            benefits_charity = str(input_data['benefits_charity'])
            benefits_charity = '' if benefits_charity == "False" or benefits_charity == '0' or benefits_charity == '' else benefits_charity
            criterion8 = Q(benefits_charity=benefits_charity) if benefits_charity else Q()
        except Exception as e:
            ShowException(e)
        try:
            returns_accepted = str(input_data['returns_accepted'])
            returns_accepted = '' if returns_accepted == "False" or returns_accepted == '0' or returns_accepted == '' else returns_accepted
            criterion9 = Q(returns_accepted=returns_accepted) if returns_accepted else Q()
        except Exception as e:
            ShowException(e)

        try:
            parent_category_name = (input_data['parent_category_name'])
            parent_category_name = '' if (
                    parent_category_name == False or parent_category_name == 0 or parent_category_name == '' or parent_category_name == []) else parent_category_name
            criterion10 = Q(parent_category_name__iexact=parent_category_name) if parent_category_name else Q()
        except Exception as e:
            ShowException(e)
        try:
            our_category_name = (input_data['our_category_name'])
            our_category_name = '' if (
                    our_category_name == False or our_category_name == 0 or our_category_name == '' or our_category_name == []) else our_category_name
            criterion11 = Q(our_category_name__iexact=our_category_name) if our_category_name else Q()
        except Exception as e:
            ShowException(e)
        try:
            our_category_name_2 = (input_data['our_category_name_2'])
            our_category_name_2 = '' if (
                    our_category_name_2 == False or our_category_name_2 == 0 or our_category_name_2 == '' or our_category_name_2 == []) else our_category_name_2
            criterion12 = Q(our_category_name_2__iexact=our_category_name_2) if our_category_name_2 else Q()
            criterion12 = criterion11 | criterion12
        except Exception as e:
            ShowException(e)

        try:
            keywords = (input_data['keywords'])
            keywords = [] if keywords == False or keywords == 0 or keywords == '' else keywords
            criterion13 = Q(reduce(operator.or_, (Q(keywords__icontains=x) for x in keywords))) if keywords else Q()
        except Exception as e:
            ShowException(e)

        try:
            collar = (input_data['collar'])
            collar = [] if collar == False or collar == 0 or collar == '' else collar
            criterion14 = Q(reduce(operator.or_, (Q(collar__icontains=x) for x in collar))) if collar else Q()
        except Exception as e:
            ShowException(e)

        try:
            cuff_style = (input_data['cuff_style'])
            cuff_style = [] if cuff_style == False or cuff_style == 0 or cuff_style == '' else cuff_style
            criterion15 = Q(
                reduce(operator.or_, (Q(cuff_style__icontains=x) for x in cuff_style))) if cuff_style else Q()
        except Exception as e:
            ShowException(e)

        try:
            fastening_type = (input_data['fastening_type'])
            fastening_type = [] if fastening_type == False or fastening_type == 0 or fastening_type == '' else fastening_type
            criterion16 = Q(reduce(operator.or_,
                                   (Q(fastening_type__icontains=x) for x in fastening_type))) if fastening_type else Q()
        except Exception as e:
            ShowException(e)

        try:
            theme = (input_data['theme'])
            theme = [] if theme == False or theme == 0 or theme == '' else theme
            criterion17 = Q(reduce(operator.or_, (Q(theme__icontains=x) for x in theme))) if theme else Q()
        except Exception as e:
            ShowException(e)

        try:
            sleeve_type = (input_data['sleeve_type'])
            sleeve_type = [] if sleeve_type == False or sleeve_type == 0 or sleeve_type == '' else sleeve_type
            criterion18 = Q(
                reduce(operator.or_, (Q(sleeve_type__icontains=x) for x in sleeve_type))) if sleeve_type else Q()
        except Exception as e:
            ShowException(e)

        try:
            sleeve_length = (input_data['sleeve_length'])
            sleeve_length = [] if sleeve_length == False or sleeve_length == 0 or sleeve_length == '' else sleeve_length
            criterion19 = Q(
                reduce(operator.or_, (Q(sleeve_length__icontains=x) for x in sleeve_length))) if sleeve_length else Q()
        except Exception as e:
            ShowException(e)

        try:
            occasion = (input_data['occasion'])
            occasion = [] if occasion == False or occasion == 0 or occasion == '' else occasion
            criterion20 = Q(reduce(operator.or_, (Q(occasion__icontains=x) for x in occasion))) if occasion else Q()
        except Exception as e:
            ShowException(e)

        try:
            neckline = (input_data['neckline'])
            neckline = [] if neckline == False or neckline == 0 or neckline == '' else neckline
            criterion21 = Q(reduce(operator.or_, (Q(neckline__icontains=x) for x in neckline))) if neckline else Q()
        except Exception as e:
            ShowException(e)
        try:
            pattern = (input_data['pattern'])
            pattern = [] if pattern == False or pattern == 0 or pattern == '' else pattern
            criterion22 = Q(reduce(operator.or_, (Q(pattern__icontains=x) for x in pattern))) if pattern else Q()
        except Exception as e:
            ShowException(e)

        try:
            garment_care = (input_data['garment_care'])
            garment_care = [] if garment_care == False or garment_care == 0 or garment_care == '' else garment_care
            criterion23 = Q(
                reduce(operator.or_, (Q(garment_care__icontains=x) for x in garment_care))) if garment_care else Q()
        except Exception as e:
            ShowException(e)

        try:
            season = (input_data['season'])
            season = [] if season == False or season == 0 or season == '' else season
            criterion24 = Q(reduce(operator.or_, (Q(season__icontains=x) for x in season))) if season else Q()
        except Exception as e:
            ShowException(e)

        try:
            feature = (input_data['feature'])
            feature = [] if feature == False or feature == 0 or feature == '' else feature
            criterion25 = Q(reduce(operator.or_, (Q(feature__icontains=x) for x in feature))) if feature else Q()
        except Exception as e:
            ShowException(e)

        try:
            fabric_type = (input_data['fabric_type'])
            fabric_type = [] if fabric_type == False or fabric_type == 0 or fabric_type == '' else fabric_type
            criterion26 = Q(
                reduce(operator.or_, (Q(fabric_type__icontains=x) for x in fabric_type))) if fabric_type else Q()
        except Exception as e:
            ShowException(e)

        try:
            embellishment = (input_data['embellishment'])
            embellishment = [] if embellishment == False or embellishment == 0 or embellishment == '' else embellishment
            criterion27 = Q(
                reduce(operator.or_, (Q(embellishment__icontains=x) for x in embellishment))) if embellishment else Q()
        except Exception as e:
            ShowException(e)

        try:
            dress_style = (input_data['dress_style'])
            dress_style = [] if dress_style == False or dress_style == 0 or dress_style == '' else dress_style
            criterion28 = Q(
                reduce(operator.or_, (Q(dress_style__icontains=x) for x in dress_style))) if dress_style else Q()
        except Exception as e:
            ShowException(e)

        try:
            dress_length = (input_data['dress_length'])
            dress_length = [] if dress_length == False or dress_length == 0 or dress_length == '' else dress_length
            criterion29 = Q(
                reduce(operator.or_, (Q(dress_length__icontains=x) for x in dress_length))) if dress_length else Q()
        except Exception as e:
            ShowException(e)

        try:
            closure = (input_data['closure'])
            closure = [] if closure == False or closure == 0 or closure == '' else closure
            criterion30 = Q(reduce(operator.or_, (Q(closure__icontains=x) for x in closure))) if closure else Q()
        except Exception as e:
            ShowException(e)

        try:
            characters = (input_data['characters'])
            characters = [] if characters == False or characters == 0 or characters == '' else characters
            criterion31 = Q(
                reduce(operator.or_, (Q(characters__icontains=x) for x in characters))) if characters else Q()
        except Exception as e:
            ShowException(e)

        try:
            fit_type = (input_data['fit_type'])
            fit_type = [] if fit_type == False or fit_type == 0 or fit_type == '' else fit_type
            criterion32 = Q(reduce(operator.or_, (Q(fit_type__icontains=x) for x in fit_type))) if fit_type else Q()
        except Exception as e:
            ShowException(e)

        try:
            material = (input_data['material'])
            material = [] if material == False or material == 0 or material == '' else material
            criterion33 = Q(reduce(operator.or_, (Q(material__icontains=x) for x in material))) if material else Q()
        except Exception as e:
            ShowException(e)

        try:
            display_color = (input_data['display_color'])
            display_color = [] if display_color == False or display_color == 0 or display_color == '' else display_color
            criterion34 = Q(
                reduce(operator.or_, (Q(display_color__icontains=x) for x in display_color))) if display_color else Q()
        except Exception as e:
            ShowException(e)

        try:
            multicolor = str(input_data['multicolor'])
            multicolor = '' if multicolor == "False" or multicolor == '0' or multicolor == '' else multicolor
            criterion35 = Q(multicolor=multicolor) if multicolor else Q()
        except Exception as e:
            ShowException(e)

        try:
            color = (input_data['color'])
            color = [] if color == False or color == 0 or color == '' else color
            criterion36 = Q(reduce(operator.or_, (Q(color__icontains=x) for x in color))) if color else Q()
        except Exception as e:
            ShowException(e)

        try:
            plus_size = (input_data['plus_size'])
            plus_size = [] if plus_size == False or plus_size == 0 or plus_size == '' else plus_size
            criterion37 = Q(reduce(operator.or_, (Q(plus_size__icontains=x) for x in plus_size))) if plus_size else Q()
        except Exception as e:
            ShowException(e)

        try:
            tall_size = (input_data['tall_size'])
            tall_size = [] if tall_size == False or tall_size == 0 or tall_size == '' else tall_size
            criterion38 = Q(reduce(operator.or_, (Q(tall_size__icontains=x) for x in tall_size))) if tall_size else Q()
        except Exception as e:
            ShowException(e)

        try:
            regular_size = (input_data['regular_size'])
            regular_size = [] if regular_size == False or regular_size == 0 or regular_size == '' else regular_size
            criterion39 = Q(
                reduce(operator.or_, (Q(regular_size__icontains=x) for x in regular_size))) if regular_size else Q()
        except Exception as e:
            ShowException(e)

        try:
            petite_size = (input_data['petite_size'])
            petite_size = [] if petite_size == False or petite_size == 0 or petite_size == '' else petite_size
            criterion40 = Q(
                reduce(operator.or_, (Q(petite_size__icontains=x) for x in petite_size))) if petite_size else Q()
        except Exception as e:
            ShowException(e)

        try:
            short_size = (input_data['short_size'])
            short_size = [] if short_size == False or short_size == 0 or short_size == '' else short_size
            criterion41 = Q(
                reduce(operator.or_, (Q(short_size__icontains=x) for x in short_size))) if short_size else Q()
        except Exception as e:
            ShowException(e)

        try:
            long_size = (input_data['long_size'])
            long_size = [] if long_size == False or long_size == 0 or long_size == '' else long_size
            criterion42 = Q(
                reduce(operator.or_, (Q(long_size__icontains=x) for x in long_size))) if long_size else Q()
        except Exception as e:
            ShowException(e)

        try:
            xlong_size = (input_data['x_long_size'])
            xlong_size = [] if xlong_size == False or xlong_size == 0 or xlong_size == '' else xlong_size
            criterion43 = Q(
                reduce(operator.or_, (Q(xlong_size__icontains=x) for x in xlong_size))) if xlong_size else Q()
        except Exception as e:
            ShowException(e)

        try:
            price = str(input_data['price'])
            start_price = float(price.split('-')[0])
            end_price = float(price.split('-')[1])
            criterion44 = (Q(sale_price__gt=0, sale_price__range=(start_price, end_price)) | Q(sale_price=0,
                                                                                               price__range=(
                                                                                                   start_price,
                                                                                                   end_price))) if price else Q()
        except Exception as e:
            ShowException(e)

        try:
            name = (input_data['name'])
            name = [] if name == False or name == 0 or name == '' else name
            criterion45 = Q(reduce(operator.or_, (Q(name__icontains=x) for x in name))) if name else Q()
        except Exception as e:
            ShowException(e)

        endlimit = page * products_per_page
        start_limit = endlimit - products_per_page
        result = Products.objects.filter(criterion1, criterion2, criterion3, criterion4, criterion5, criterion6,
                                         criterion7, criterion8, criterion9, criterion10, criterion12, criterion13,
                                         criterion14, criterion15, criterion16, criterion17, criterion18, criterion19,
                                         criterion20, criterion21, criterion22, criterion23, criterion24, criterion25,
                                         criterion26, criterion27, criterion28, criterion29, criterion30, criterion31,
                                         criterion32, criterion33, criterion34, criterion35, criterion36, criterion37,
                                         criterion38, criterion39, criterion40, criterion41, criterion42, criterion43,
                                         criterion44, criterion45).order_by(name_asc, price_asc, sale_price_asc)
        total_products = result.count()
        data = result[start_limit:endlimit]
        try:
            return_data = []
            for row in data:
                is_favourite = False
                is_email_alert = False
                if row.shipping_offer_type:
                    shipping = row.shipping_offer_type.split(' | ')[0]
                    if shipping:
                        shipping_label = row.shipping_offer_label.split(' | ')[0]
                try:
                    if input_data['userid'] != False and input_data['userid'] != '' and input_data[
                        'userid'] != False and input_data['userid'] != []:
                        if Favourite_Ads.objects.filter(user_id=input_data['userid'],
                                                        product_id=row.id).exists() == True:
                            is_favourite = True
                        if Email_Alerts.objects.filter(user_id=input_data['userid'],
                                                       product_id=row.id).exists() == True:
                            is_email_alert = True

                except Exception as e:
                    ShowException(e)

                return_data.append([
                    {
                        "id": row.id,
                        "product_url": row.product_url,
                        "name": row.name,
                        "image": row.image,
                        "product_slug": row.product_slug,
                        "petite_size": row.petite_size,
                        "short_size": row.short_size,
                        "long_size": row.long_size,
                        "xlong_size": row.x_long_size,
                        "regular_size": row.regular_size,
                        "tall_size": row.tall_size,
                        "plus_size": row.plus_size,
                        "color": row.color,
                        "multicolor": row.multicolor,
                        "display_color": row.display_color,
                        "material": row.material,
                        "brand": row.brand,
                        "brand_slug ": row.brand_slug,
                        "price": row.price,
                        "price_highest": row.price_highest,
                        "currency": row.currency,
                        "sale_price": row.sale_price,
                        "sale_price_highest": row.sale_price_highest,
                        "store_name": row.store_name,
                        "store_url": row.store_url,
                        "discount_percentage": row.discount_percentage,
                        "discount_percentage_highest": row.discount_percentage_highest,
                        "promo_offer_type": row.promo_offer_type,
                        "promo_offer_label": row.promo_offer_label,
                        "price_offer_type": row.price_offer_type,
                        "price_offer_label": row.price_offer_label,
                        "shipping_offer_type": row.shipping_offer_type,
                        "shipping_offer_label": row.shipping_offer_label,
                        "other_offer_type": row.other_offer_type,
                        "other_offer_label": row.other_offer_label,
                        "parent_category_name": row.parent_category_name,
                        "parent_category_name_2": row.parent_category_name_2,
                        "shipping": shipping_label,
                        "promos": row.promo_dict,
                        "last_scrapper_update": row.last_scrapper_update,
                        "is_favourite": is_favourite,
                        "is_email_alert": is_email_alert
                    }])
            context = {'Message': 'Success', 'page': page, 'TotalProducts': total_products,
                       'FetchedProducts': len(return_data), 'return_data': return_data}
        except Exception as e:
            ShowException(e)
            error = 'Error in getting data,check format of request body and try again.'
            context = {'Message': error, 'return_data': []}
        return Response(context)
    except Exception as e:
        error = 'Error in getting data,check format of request body and try again.'
        context = {'Message': error, 'return_data': []}
        ShowException(e)
        return Response(context)


@api_view(['GET', 'POST'])
@csrf_exempt
def GetProductsFilters(request):
    try:
        criterion1, criterion2, criterion3, criterion4, criterion5, criterion6, criterion7, criterion8, criterion9, criterion10 = Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q()
        criterion11, criterion12, criterion13, criterion14, criterion15, criterion16, criterion17, criterion18, criterion19, criterion20 = Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q()
        criterion21, criterion22, criterion23, criterion24, criterion25, criterion26, criterion27, criterion28, criterion29, criterion30 = Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q()
        criterion31, criterion32, criterion33, criterion34, criterion35, criterion36, criterion37, criterion38, criterion39, criterion40 = Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q(), Q()
        criterion41, criterion42, criterion43, criterion44, criterion45, criterion46 = Q(), Q(), Q(), Q(), Q(), Q()

        WhereParent_category_name = ""
        input_data = request.data
        try:
            if len(input_data) == 0:
                error = "Error in getting data, request body is empty."
                context = {'Message': error, 'return_data': []}
                return Response(context)
        except:
            error = "Error in getting data, request body is empty."
            context = {'Message': error, 'return_data': []}
            return Response(context)
        try:
            store_id = (input_data['store_id'])
            store_id = '' if (store_id == "False" or (store_id) == '0' or store_id == '') else store_id
            # criterion1 = Q(store_id=store_id) if store_id and type(store_id)==int else  Q()
            if store_id and type(store_id) == int:
                criterion1 = Q(store_id=store_id)
            elif store_id and type(store_id) == str:
                criterion1 = Q(store_name__iexact=store_id)
            else:
                Q()
        except Exception as e:
            ShowException(e)
        try:
            brand_id = (input_data['brand_id'])
            brand_id = [] if (brand_id == False or brand_id == 0 or brand_id == '') else brand_id
            # criterion2= Q(reduce(operator.or_, (Q(brand_id=x) for x in brand_id))) if brand_id and type(brand_id[0])==int  else Q()
            if brand_id and type(brand_id[0]) == int:
                criterion2 = Q(reduce(operator.or_, (Q(brand_id=x) for x in brand_id)))
            elif brand_id and type(brand_id[0]) == str:
                criterion2 = Q(reduce(operator.or_, (Q(brand__iexact=x) for x in brand_id)))
            else:
                Q()
        except Exception as e:
            ShowException(e)

        try:
            coupon_code = (input_data['coupon_code'])
            coupon_code = [] if coupon_code == False or coupon_code == 0 or coupon_code == '' else coupon_code
            criterion3 = Q(
                reduce(operator.or_, (Q(coupon_code__icontains=x) for x in coupon_code))) if coupon_code else Q()
        except Exception as e:
            ShowException(e)
        try:
            offer_type_label = (input_data['offer_type_label'])
            offer_type_label = [] if offer_type_label == False or offer_type_label == 0 or offer_type_label == '' else offer_type_label
            criterion4 = Q(reduce(operator.or_, (Q(offer_type_label__icontains=str(x)) for x in
                                                 offer_type_label))) if offer_type_label else Q()
        except Exception as e:
            ShowException(e)
        try:
            offer_type = (input_data['offer_type'])
            offer_type = [] if offer_type == False or offer_type == 0 or offer_type == '' else offer_type
            criterion5 = Q(
                reduce(operator.or_, (Q(offer_type__icontains=x) for x in offer_type))) if offer_type else Q()
        except Exception as e:
            ShowException(e)
        try:
            authenticity_guarantee = str(input_data['authenticity_guarantee'])
            authenticity_guarantee = '' if authenticity_guarantee == "False" or authenticity_guarantee == '0' or authenticity_guarantee == '' else authenticity_guarantee
            criterion6 = Q(authenticity_guarantee=authenticity_guarantee) if authenticity_guarantee else Q()
        except Exception as e:
            ShowException(e)
        try:
            climate_pledge_friendly = str(input_data['climate_pledge_friendly'])
            climate_pledge_friendly = '' if climate_pledge_friendly == "False" or climate_pledge_friendly == '0' or climate_pledge_friendly == '' else climate_pledge_friendly
            criterion7 = Q(climate_pledge_friendly=climate_pledge_friendly) if climate_pledge_friendly else Q()
        except Exception as e:
            ShowException(e)
        try:
            benefits_charity = str(input_data['benefits_charity'])
            benefits_charity = '' if benefits_charity == "False" or benefits_charity == '0' or benefits_charity == '' else benefits_charity
            criterion8 = Q(benefits_charity=benefits_charity) if benefits_charity else Q()

        except Exception as e:
            ShowException(e)
        try:
            returns_accepted = str(input_data['returns_accepted'])
            returns_accepted = '' if returns_accepted == "False" or returns_accepted == '0' or returns_accepted == '' else returns_accepted
            criterion9 = Q(returns_accepted=returns_accepted) if returns_accepted else Q()
        except Exception as e:
            ShowException(e)
        try:
            parent_category_name = (input_data['parent_category_name'])
            parent_category_name = '' if (
                    parent_category_name == False or parent_category_name == 0 or parent_category_name == '' or parent_category_name == []) else parent_category_name
            criterion10 = Q(parent_category_name__iexact=parent_category_name) | Q(
                parent_category_name_2__iexact=parent_category_name) if parent_category_name else Q()
        except Exception as e:
            ShowException(e)
        try:
            our_category_name = (input_data['our_category_name'])
            our_category_name = '' if (
                    our_category_name == False or our_category_name == 0 or our_category_name == '' or our_category_name == []) else our_category_name
            criterion11 = Q(our_category_name__iexact=our_category_name) | Q(
                our_category_name_2__iexact=our_category_name) if our_category_name else Q()
        except Exception as e:
            ShowException(e)
        try:
            our_category_name_2 = (input_data['our_category_name_2'])
            our_category_name_2 = '' if (
                    our_category_name_2 == False or our_category_name_2 == 0 or our_category_name_2 == '' or our_category_name_2 == []) else our_category_name_2
            criterion12 = Q(our_category_name_2__iexact=our_category_name_2) | Q(
                our_category_name_2__iexact=our_category_name_2) if our_category_name_2 else Q()
            criterion12 = criterion11 | criterion12

        except Exception as e:
            ShowException(e)
        try:
            keywords = (input_data['keywords'])
            keywords = [] if keywords == False or keywords == 0 or keywords == '' else keywords
            criterion13 = Q(reduce(operator.or_, (Q(keywords__icontains=x) for x in keywords))) if keywords else Q()
        except Exception as e:
            ShowException(e)
        try:
            collar = (input_data['collar'])
            collar = [] if collar == False or collar == 0 or collar == '' else collar
            criterion14 = Q(reduce(operator.or_, (Q(collar__icontains=x) for x in collar))) if collar else Q()
        except Exception as e:
            ShowException(e)
        try:
            cuff_style = (input_data['cuff_style'])
            cuff_style = [] if cuff_style == False or cuff_style == 0 or cuff_style == '' else cuff_style
            criterion15 = Q(
                reduce(operator.or_, (Q(cuff_style__icontains=x) for x in cuff_style))) if cuff_style else Q()
        except Exception as e:
            ShowException(e)
        try:
            fastening_type = (input_data['fastening_type'])
            fastening_type = [] if fastening_type == False or fastening_type == 0 or fastening_type == '' else fastening_type
            criterion16 = Q(reduce(operator.or_,
                                   (Q(fastening_type__icontains=x) for x in fastening_type))) if fastening_type else Q()
        except Exception as e:
            ShowException(e)
        try:
            theme = (input_data['theme'])
            theme = [] if theme == False or theme == 0 or theme == '' else theme
            criterion17 = Q(reduce(operator.or_, (Q(theme__icontains=x) for x in theme))) if theme else Q()
        except Exception as e:
            ShowException(e)
        try:
            sleeve_type = (input_data['sleeve_type'])
            sleeve_type = [] if sleeve_type == False or sleeve_type == 0 or sleeve_type == '' else sleeve_type
            criterion18 = Q(
                reduce(operator.or_, (Q(sleeve_type__icontains=x) for x in sleeve_type))) if sleeve_type else Q()
        except Exception as e:
            ShowException(e)
        try:
            sleeve_length = (input_data['sleeve_length'])
            sleeve_length = [] if sleeve_length == False or sleeve_length == 0 or sleeve_length == '' else sleeve_length
            criterion19 = Q(
                reduce(operator.or_, (Q(sleeve_length__icontains=x) for x in sleeve_length))) if sleeve_length else Q()
        except Exception as e:
            ShowException(e)
        try:
            occasion = (input_data['occasion'])
            occasion = [] if occasion == False or occasion == 0 or occasion == '' else occasion
            criterion20 = Q(reduce(operator.or_, (Q(occasion__icontains=x) for x in occasion))) if occasion else Q()
        except Exception as e:
            ShowException(e)
        try:
            neckline = (input_data['neckline'])
            neckline = [] if neckline == False or neckline == 0 or neckline == '' else neckline
            criterion21 = Q(reduce(operator.or_, (Q(neckline__icontains=x) for x in neckline))) if neckline else Q()
        except Exception as e:
            ShowException(e)
        try:
            pattern = (input_data['pattern'])
            pattern = [] if pattern == False or pattern == 0 or pattern == '' else pattern
            criterion22 = Q(reduce(operator.or_, (Q(pattern__icontains=x) for x in pattern))) if pattern else Q()
        except Exception as e:
            ShowException(e)
        try:
            garment_care = (input_data['garment_care'])
            garment_care = [] if garment_care == False or garment_care == 0 or garment_care == '' else garment_care
            criterion23 = Q(
                reduce(operator.or_, (Q(garment_care__icontains=x) for x in garment_care))) if garment_care else Q()
        except Exception as e:
            ShowException(e)
        try:
            season = (input_data['season'])
            season = [] if season == False or season == 0 or season == '' else season
            criterion24 = Q(reduce(operator.or_, (Q(season__icontains=x) for x in season))) if season else Q()
        except Exception as e:
            ShowException(e)
        try:
            feature = (input_data['feature'])
            feature = [] if feature == False or feature == 0 or feature == '' else feature
            criterion25 = Q(reduce(operator.or_, (Q(feature__icontains=x) for x in feature))) if feature else Q()
        except Exception as e:
            ShowException(e)
        try:
            fabric_type = (input_data['fabric_type'])
            fabric_type = [] if fabric_type == False or fabric_type == 0 or fabric_type == '' else fabric_type
            criterion26 = Q(
                reduce(operator.or_, (Q(fabric_type__icontains=x) for x in fabric_type))) if fabric_type else Q()
        except Exception as e:
            ShowException(e)
        try:
            embellishment = (input_data['embellishment'])
            embellishment = [] if embellishment == False or embellishment == 0 or embellishment == '' else embellishment
            criterion27 = Q(
                reduce(operator.or_, (Q(embellishment__icontains=x) for x in embellishment))) if embellishment else Q()
        except Exception as e:
            ShowException(e)
        try:
            dress_style = (input_data['dress_style'])
            dress_style = [] if dress_style == False or dress_style == 0 or dress_style == '' else dress_style
            criterion28 = Q(
                reduce(operator.or_, (Q(dress_style__icontains=x) for x in dress_style))) if dress_style else Q()
            print(criterion28)
        except Exception as e:
            ShowException(e)
        try:
            dress_length = (input_data['dress_length'])
            dress_length = [] if dress_length == False or dress_length == 0 or dress_length == '' else dress_length
            criterion29 = Q(
                reduce(operator.or_, (Q(dress_length__icontains=x) for x in dress_length))) if dress_length else Q()
        except Exception as e:
            ShowException(e)
        try:
            closure = (input_data['closure'])
            closure = [] if closure == False or closure == 0 or closure == '' else closure
            criterion30 = Q(reduce(operator.or_, (Q(closure__icontains=x) for x in closure))) if closure else Q()
        except Exception as e:
            ShowException(e)
        try:
            characters = (input_data['characters'])
            characters = [] if characters == False or characters == 0 or characters == '' else characters
            criterion31 = Q(
                reduce(operator.or_, (Q(characters__icontains=x) for x in characters))) if characters else Q()
        except Exception as e:
            ShowException(e)
        try:
            fit_type = (input_data['fit_type'])
            fit_type = [] if fit_type == False or fit_type == 0 or fit_type == '' else fit_type
            criterion32 = Q(reduce(operator.or_, (Q(fit_type__icontains=x) for x in fit_type))) if fit_type else Q()
        except Exception as e:
            ShowException(e)
        try:
            material = (input_data['material'])
            material = [] if material == False or material == 0 or material == '' else material
            criterion33 = Q(reduce(operator.or_, (Q(material__icontains=x) for x in material))) if material else Q()
        except Exception as e:
            ShowException(e)
        try:
            display_color = (input_data['display_color'])
            display_color = [] if display_color == False or display_color == 0 or display_color == '' else display_color
            criterion34 = Q(
                reduce(operator.or_, (Q(display_color__icontains=x) for x in display_color))) if display_color else Q()
        except Exception as e:
            ShowException(e)
        try:
            multicolor = str(input_data['multicolor'])
            multicolor = '' if multicolor == "False" or multicolor == '0' or multicolor == '' else multicolor
            criterion35 = Q(multicolor=multicolor) if multicolor else Q()
        except Exception as e:
            ShowException(e)
        try:
            color = (input_data['color'])
            color = [] if color == False or color == 0 or color == '' else color
            criterion36 = Q(reduce(operator.or_, (Q(color__icontains=x) for x in color))) if color else Q()
        except Exception as e:
            ShowException(e)
        try:
            plus_size = (input_data['plus_size'])
            plus_size = [] if plus_size == False or plus_size == 0 or plus_size == '' else plus_size
            criterion37 = Q(reduce(operator.or_, (Q(plus_size__icontains=x) for x in plus_size))) if plus_size else Q()
        except Exception as e:
            ShowException(e)
        try:
            tall_size = (input_data['tall_size'])
            tall_size = [] if tall_size == False or tall_size == 0 or tall_size == '' else tall_size
            criterion38 = Q(reduce(operator.or_, (Q(tall_size__icontains=x) for x in tall_size))) if tall_size else Q()
        except Exception as e:
            ShowException(e)
        try:
            regular_size = (input_data['regular_size'])
            regular_size = [] if regular_size == False or regular_size == 0 or regular_size == '' else regular_size
            criterion39 = Q(
                reduce(operator.or_, (Q(regular_size__icontains=x) for x in regular_size))) if regular_size else Q()
        except Exception as e:
            ShowException(e)
        try:
            petite_size = (input_data['petite_size'])
            petite_size = [] if petite_size == False or petite_size == 0 or petite_size == '' else petite_size
            criterion40 = Q(
                reduce(operator.or_, (Q(petite_size__icontains=x) for x in petite_size))) if petite_size else Q()
        except Exception as e:
            ShowException(e)

        try:
            short_size = (input_data['short_size'])
            short_size = [] if short_size == False or short_size == 0 or short_size == '' else short_size
            criterion44 = Q(
                reduce(operator.or_, (Q(short_size__icontains=x) for x in short_size))) if short_size else Q()
        except Exception as e:
            ShowException(e)

        try:
            long_size = (input_data['long_size'])
            long_size = [] if long_size == False or long_size == 0 or long_size == '' else long_size
            criterion45 = Q(
                reduce(operator.or_, (Q(long_size__icontains=x) for x in long_size))) if long_size else Q()
        except Exception as e:
            ShowException(e)

        try:
            xlong_size = (input_data['xlong_size'])
            xlong_size = [] if xlong_size == False or xlong_size == 0 or xlong_size == '' else xlong_size
            criterion46 = Q(
                reduce(operator.or_, (Q(xlong_size__icontains=x) for x in xlong_size))) if xlong_size else Q()
        except Exception as e:
            ShowException(e)

        try:
            name = (input_data['name'])
            name = [] if name == False or name == 0 or name == '' else name
            criterion41 = Q(reduce(operator.or_, (Q(name__icontains=x) for x in name))) if name else Q()
        except Exception as e:
            ShowException(e)
        try:
            price = str(input_data['price'])
            start_price = float(price.split('-')[0])
            end_price = float(price.split('-')[1])
            criterion42 = (Q(sale_price__gt=0, sale_price__range=(start_price, end_price)) | Q(sale_price=0,
                                                                                               price__range=(
                                                                                                   start_price,
                                                                                                   end_price))) if price else Q()
        except Exception as e:
            ShowException(e)
        result = Products.objects.filter(criterion1, criterion2, criterion3, criterion4, criterion5, criterion6,
                                         criterion7, criterion8, criterion9, criterion10,
                                         criterion11, criterion12, criterion13, criterion14, criterion15, criterion16,
                                         criterion17, criterion18, criterion19, criterion20,
                                         criterion21, criterion22, criterion23, criterion24, criterion25, criterion26,
                                         criterion27, criterion28, criterion29, criterion30,
                                         criterion31, criterion32, criterion33, criterion34, criterion35, criterion36,
                                         criterion37, criterion38, criterion39, criterion40, criterion41, criterion42,
                                         criterion44, criterion45, criterion46,
                                         )
        total_products = result.count()
        petite_size, regular_size, tall_size, plus_size, short_size, long_size, xlong_size, neckline = [], [], [], [], [], [], [], []
        color, material, fit_type, characters, closure = [], [], [], [], []
        dress_length, dress_style, embellishment, feature, season = [], [], [], [], []
        garment_care, pattern, occasion, sleeve_length, sleeve_type = [], [], [], [], []
        theme, fastening_type, cuff_style, collar, brand = [], [], [], [], []
        our_category_name, parent_category_name, offer_type, store, = [], [], [], []
        benefits_charity, climate_pledge_friendly, authenticity_guarantee, returns_accepted = [], [], [], []
        prices = []
        for row in result:
            if row.sale_price == 0:
                prices.append(row.price)
            else:
                prices.append(row.sale_price)
            try:
                for r in row.petite_size.split('|'):
                    if r: petite_size.append(r.strip())
            except:
                pass
            try:
                for r in row.regular_size.split('|'):
                    if r: regular_size.append(r.strip())
            except:
                pass
            try:
                for r in row.tall_size.split('|'):
                    if r: tall_size.append(r.strip())
            except:
                pass
            try:
                for r in row.plus_size.split('|'):
                    if r: plus_size.append(r.strip())
            except:
                pass

            try:
                for r in row.short_size.split('|'):
                    if r: short_size.append(r.strip())
            except:
                pass

            try:
                for r in row.long_size.split('|'):
                    if r: long_size.append(r.strip())
            except:
                pass

            try:
                for r in row.xlong_size.split('|'):
                    if r: xlong_size.append(r.strip())
            except:
                pass

            try:
                for r in row.neckline.split('|'):
                    if r: neckline.append(r.strip())
            except:
                pass
            try:
                for r in row.color.split('|'):
                    if r: color.append(r.strip())
            except:
                pass
            try:
                for r in row.material.split('|'):
                    if r: material.append(r.strip())
            except:
                pass
            try:
                for r in row.fit_type.split('|'):
                    if r: fit_type.append(r.strip())
            except:
                pass
            try:
                for r in row.characters.split('|'):
                    if r: characters.append(r.strip())
            except:
                pass
            try:
                for r in row.closure.split('|'):
                    if r: closure.append(r.strip())
            except:
                pass
            try:
                for r in row.dress_length.split('|'):
                    if r: dress_length.append(r.strip())
            except:
                pass
            try:
                for r in row.dress_style.split('|'):
                    if r: dress_style.append(r.strip())
            except:
                pass
            try:
                for r in row.embellishment.split('|'):
                    if r: embellishment.append(r.strip())
            except:
                pass
            try:
                for r in row.feature.split('|'):
                    if r: feature.append(r.strip())
            except:
                pass
            try:
                for r in row.season.split('|'):
                    if r: season.append(r.strip())
            except:
                pass
            try:
                for r in row.garment_care.split('|'):
                    if r: garment_care.append(r.strip())
            except:
                pass
            try:
                for r in row.pattern.split('|'):
                    if r: pattern.append(r.strip())
            except:
                pass
            try:
                for r in row.occasion.split('|'):
                    if r: occasion.append(r.strip())
            except:
                pass
            try:
                for r in row.sleeve_length.split('|'):
                    if r: sleeve_length.append(r.strip())
            except:
                pass
            try:
                for r in row.sleeve_type.split('|'):
                    if r: sleeve_type.append(r.strip())
            except:
                pass
            try:
                for r in row.theme.split('|'):
                    if r: theme.append(r.strip())
            except:
                pass
            try:
                for r in row.fastening_type.split('|'):
                    if r: fastening_type.append(r.strip())
            except:
                pass
            try:
                for r in row.cuff_style.split('|'):
                    if r: cuff_style.append(r.strip())
            except:
                pass
            try:
                for r in row.collar.split('|'):
                    if r: collar.append(r.strip())
            except:
                pass
            try:
                for r in row.brand.split('|'):
                    if r: brand.append(r.strip())
            except Exception as e:
                pass
            try:
                for r in row.our_category_name_2.split('|'):
                    if r: our_category_name.append(r.strip())
            except:
                pass
            try:
                for r in row.our_category_name.split('|'):
                    if r: our_category_name.append(r.strip())
            except:
                pass
            try:
                for r in row.parent_category_name.split('|'):
                    if r: parent_category_name.append(r.strip())
            except:
                pass
            try:
                for r in row.store_name.split('|'):
                    if r: store.append(r.strip())
            except:
                pass
            try:
                for r in row.offer_type.split('|'):
                    if r: offer_type.append(r.strip())
            except:
                pass

            try:
                if row.returns_accepted: returns_accepted.append(row.returns_accepted)
            except Exception as e:
                pass
            try:
                if row.benefits_charity: benefits_charity.append(row.benefits_charity)
            except:
                pass
            try:
                if row.climate_pledge_friendly: climate_pledge_friendly.append(row.climate_pledge_friendly)

            except:
                pass
            try:
                if row.authenticity_guarantee: authenticity_guarantee.append(row.authenticity_guarantee)
            except:
                pass

        petite_size_count = dict(Counter(petite_size))
        regular_size_count = dict(Counter(regular_size))
        tall_size_count = dict(Counter(tall_size))
        plus_size_count = dict(Counter(plus_size))
        short_size_count = dict(Counter(short_size))
        long_size_count = dict(Counter(long_size))
        xlong_size_count = dict(Counter(xlong_size))
        neckline_count = dict(Counter(neckline))
        color_count = dict(Counter(color))
        material_count = dict(Counter(material))
        fit_type_count = dict(Counter(fit_type))
        characters_count = dict(Counter(characters))
        closure_count = dict(Counter(closure))
        dress_length_count = dict(Counter(dress_length))
        dress_style_count = dict(Counter(dress_style))
        embellishment_count = dict(Counter(embellishment))
        feature_count = dict(Counter(feature))
        season_count = dict(Counter(season))
        garment_care_count = dict(Counter(garment_care))
        pattern_count = dict(Counter(pattern))
        occasion_count = dict(Counter(occasion))
        sleeve_type_count = dict(Counter(sleeve_type))
        theme_count = dict(Counter(theme))
        fastening_type_count = dict(Counter(fastening_type))
        cuff_style_count = dict(Counter(cuff_style))
        brand_count = dict(Counter(brand))
        our_category_name_count = dict(Counter(our_category_name))
        parent_category_name_count = dict(Counter(parent_category_name))
        offer_type_count = dict(Counter(offer_type))
        store_count = dict(Counter(store))
        collar_count = dict(Counter(collar))
        brand_count = dict(Counter(brand))
        sleeve_length_count = dict(Counter(sleeve_length))
        ############################################
        # petite_size_count= {i:petite_size.count(i) for i in petite_size}
        # regular_size_count= {i:regular_size.count(i) for i in regular_size}
        # tall_size_count= {i:tall_size.count(i) for i in tall_size}
        # plus_size_count= {i:plus_size.count(i) for i in plus_size}
        # neckline_count= {i:neckline.count(i) for i in neckline}
        # color_count= {i:color.count(i) for i in color}
        # material_count= {i:material.count(i) for i in material}
        # fit_type_count= {i:fit_type.count(i) for i in fit_type}
        # characters_count= {i:characters.count(i) for i in characters}
        # closure_count= {i:closure.count(i) for i in closure}
        # dress_length_count= {i:dress_length.count(i) for i in dress_length}
        # dress_style_count= {i:dress_style.count(i) for i in dress_style}
        # embellishment_count= {i:embellishment.count(i) for i in embellishment}
        # feature_count= {i:feature.count(i) for i in feature}
        # season_count= {i:season.count(i) for i in season}
        # garment_care_count= {i:garment_care.count(i) for i in garment_care}
        # pattern_count= {i:pattern.count(i) for i in pattern}
        # occasion_count= {i:occasion.count(i) for i in occasion}
        # sleeve_length_count= {i:sleeve_length.count(i) for i in sleeve_length}
        # sleeve_type_count= {i:sleeve_type.count(i) for i in sleeve_type}
        # theme_count= {i:theme.count(i) for i in theme}
        # fastening_type_count= {i:fastening_type.count(i) for i in fastening_type}
        # cuff_style_count= {i:cuff_style.count(i) for i in cuff_style}
        # collar_count= {i:collar.count(i) for i in collar}
        # brand_count= {i:brand.count(i) for i in brand}
        # our_category_name_count= {i:our_category_name.count(i) for i in our_category_name}
        # parent_category_name_count= {i:parent_category_name.count(i) for i in parent_category_name}
        # offer_type_count= {i:offer_type.count(i) for i in offer_type}
        # store_count= {i:store.count(i) for i in store}
        #######
        benefits_charity_count = len(benefits_charity)
        climate_pledge_friendly_count = len(climate_pledge_friendly)
        authenticity_guarantee_count = len(authenticity_guarantee)
        returns_accepted_count = len(returns_accepted)
        # overwrite values of list to reuse them
        petite_size, regular_size, tall_size, plus_size, short_size, long_size, xlong_size, neckline = [], [], [], [], [], [], [], []
        color, material, fit_type, characters, closure = [], [], [], [], []
        dress_length, dress_style, embellishment, feature, season = [], [], [], [], []
        garment_care, pattern, occasion, sleeve_length, sleeve_type = [], [], [], [], []
        theme, fastening_type, cuff_style, collar, brand = [], [], [], [], []
        our_category_name, parent_category_name, offer_type, store, = [], [], [], []
        for k, v in petite_size_count.items():
            petite_size.append({"name": k, "count": v})
        for k, v in regular_size_count.items():
            regular_size.append({"name": k, "count": v})
        for k, v in tall_size_count.items():
            tall_size.append({"name": k, "count": v})
        for k, v in plus_size_count.items():
            plus_size.append({"name": k, "count": v})

        for k, v in short_size_count.items():
            short_size.append({"name": k, "count": v})
        for k, v in long_size_count.items():
            long_size.append({"name": k, "count": v})
        for k, v in xlong_size_count.items():
            xlong_size.append({"name": k, "count": v})

        for k, v in neckline_count.items():
            neckline.append({"name": k, "count": v})
        for k, v in color_count.items():
            color.append({"name": k, "count": v})
        for k, v in material_count.items():
            material.append({"name": k, "count": v})
        for k, v in fit_type_count.items():
            fit_type.append({"name": k, "count": v})
        for k, v in characters_count.items():
            characters.append({"name": k, "count": v})
        for k, v in closure_count.items():
            closure.append({"name": k, "count": v})
        for k, v in dress_length_count.items():
            dress_length.append({"name": k, "count": v})
        for k, v in dress_style_count.items():
            dress_style.append({"name": k, "count": v})
        for k, v in embellishment_count.items():
            embellishment.append({"name": k, "count": v})
        for k, v in feature_count.items():
            feature.append({"name": k, "count": v})
        for k, v in season_count.items():
            season.append({"name": k, "count": v})
        for k, v in garment_care_count.items():
            garment_care.append({"name": k, "count": v})
        for k, v in pattern_count.items():
            pattern.append({"name": k, "count": v})
        for k, v in occasion_count.items():
            occasion.append({"name": k, "count": v})
        for k, v in sleeve_length_count.items():
            sleeve_length.append({"name": k, "count": v})
        for k, v in sleeve_type_count.items():
            sleeve_type.append({"name": k, "count": v})
        for k, v in theme_count.items():
            theme.append({"name": k, "count": v})
        for k, v in fastening_type_count.items():
            fastening_type.append({"name": k, "count": v})
        for k, v in cuff_style_count.items():
            cuff_style.append({"name": k, "count": v})
        for k, v in collar_count.items():
            collar.append({"name": k, "count": v})
        for k, v in brand_count.items():
            brand.append({"name": k, "count": v})
        for k, v in our_category_name_count.items():
            our_category_name.append({"name": k, "count": v})
        for k, v in parent_category_name_count.items():
            parent_category_name.append({"name": k, "count": v})
        for k, v in offer_type_count.items():
            offer_type.append({"name": k, "count": v})
        for k, v in store_count.items():
            store.append({"name": k, "count": v})
        price_range = []
        ranges = [[0, 10], [10, 30], [30, 50], [50, 100], [100, 200], [200, 500], [500, 1000]]
        for r in ranges:
            price_range.append({"name": str(r[0]) + "-" + str(r[1]),
                                "count": sum(float(num) >= r[0] and float(num) <= r[1] for num in prices)})
        price_range.append({"name": "1000+", "count": sum(float(num) >= 1000 for num in prices)})
        # bb = {"color": color, "collar": list(collar)}
        # print(collar)
        # NonEmptyContext = ["color", "collar"]
        # for aa in NonEmptyContext:
        #     if bb[aa]:
        #         bb = {
        #             str(aa): bb[aa]
        #         }
        # print('jk;: ', json.dumps(bb))
        # ss
        context = {
            "total_products": total_products,
            "petite_size": petite_size,
            "regular_size": regular_size,
            "tall_size": tall_size,
            "plus_size": plus_size,
            "short_size": short_size,
            "long_size": long_size,
            "xlong_size": xlong_size,
            "neckline": neckline,
            "color": color,
            "material": material,
            "fit_type": fit_type,
            "characters": characters,
            "closure": closure,
            "dress_length": dress_length,
            "dress_style": dress_style,
            "embellishment": embellishment,
            "feature": feature,
            "season": season,
            "pattern": pattern,
            "occasion": occasion,
            "sleeve_length": sleeve_length,
            "sleeve_type": sleeve_type,
            "theme": theme,
            "fastening_type": fastening_type,
            "cuff_style": cuff_style,
            "collar": collar,
            "brand": brand,
            "our_category_name": our_category_name,
            "parent_category_name": parent_category_name,
            "offer_type": offer_type,
            "store": store,
            "price_range": price_range,
            "show_only": [{"name": "benefits_charity", "count": benefits_charity_count},
                          {"name": "climate_pledge_friendly", "count": climate_pledge_friendly_count},
                          {"name": "authenticity_guarantee", "count": authenticity_guarantee_count},
                          {"name": "returns_accepted", "count": returns_accepted_count}]

        }
        return Response(context)
    except Exception as e:
        error = 'Error in getting data,check format of request body and try again.'
        context = {'Message': error, 'return_data': []}
        ShowException(e)
        return Response(context)


@api_view(['POST'])
@csrf_exempt
def GetProductsDetail(request):
    try:
        input_data = request.data
        try:
            if len(input_data) == 0:
                context = {'Message': "Error in getting data, request body is empty.", 'return_data': []}
                return Response(context)
        except:
            context = {'Message': "Error in getting data, request body is empty.", 'return_data': []}
            return Response(context)
        try:
            product_id = int(input_data['product_id'])
            if product_id == False or product_id == '' or not product_id:
                context = {'Message': "Error in getting data,products id is empty.", 'return_data': []}
                return Response(context)
        except:
            context = {'Message': "Error in getting data,products id is invalid.", 'return_data': []}
            return Response(context)

        row = Products.objects.get(id=product_id)
        is_favourite = False
        is_email_alert = False
        try:
            if input_data['userid'] != False and input_data['userid'] != '' and input_data['userid'] != False and \
                    input_data['userid'] != []:
                if Favourite_Ads.objects.filter(user_id=input_data['userid'],
                                                product_id=input_data['product_id']).exists() == True:
                    is_favourite = True
                if Email_Alerts.objects.filter(user_id=input_data['userid'],
                                               product_id=input_data['product_id']).exists() == True:
                    is_email_alert = True
        except Exception as e:
            ShowException(e)
        product_color_sizes_list = []
        for s in Product_Color_Sizes.objects.filter(product_id=row.id):
            product_color_sizes_list.append(
                {"id": s.id, "product_id": s.product_id.id, "color_map_id": s.color_map_id, "color_name": s.color_name,
                 "size_map_id": s.size_map_id,
                 "size_type": s.size_type, "price": s.price, "sale_price": s.sale_price
                 })

        context = {
            "id": row.id,
            "name": row.name,
            "all_images": row.all_images,
            "image": row.image,
            "product_color_sizes": product_color_sizes_list,
            "petite_size": row.petite_size,
            "plus_size": row.plus_size,
            "short_size": row.short_size,
            "long_size": row.long_size,
            "xlong_size": row.xlong_size,
            "regular_size": row.regular_size,
            "tall_size": row.tall_size,
            "material": row.material,
            "feature": row.feature,
            "dress_length": row.dress_length,
            "characters": row.characters,
            "fit_type": row.fit_type,
            "closure": row.closure,
            "dress_style": row.dress_style,
            "pattern": row.pattern,
            "neckline": row.neckline,
            "theme": row.theme,
            "fastening_type": row.fastening_type,
            "collar": row.collar,
            "cuff_style": row.cuff_style,
            "sleeve_length": row.sleeve_length,
            "sleeve_type": row.sleeve_type,
            "embellishment": row.embellishment,
            "occasion": row.occasion,
            "garment_care": row.garment_care,
            "season": row.season,
            "description": row.description,
            "brand": row.brand,
            "brand_slug ": row.brand_slug,
            "currency": row.currency,
            "price": row.price,
            "price_highest": row.price_highest,
            "sale_price": row.sale_price,
            "sale_price_highest": row.sale_price_highest,
            "store_name": row.store_name,
            "store_url": row.store_url,
            "discount_percentage": row.discount_percentage,
            "discount_percentage_highest": row.discount_percentage_highest,
            "promos": row.promo_dict,
            "last_scrapper_update": row.last_scrapper_update,
            "is_favourite": is_favourite,
            "is_email_alert": is_email_alert
        }
        return Response(context)
    except Exception as e:
        context = {'Message': 'Error in getting data,check format of request body and try again.', 'return_data': []}
        ShowException(e)
        return Response(context)


@api_view(['GET', 'POST'])
@csrf_exempt
def SetProductAlert(request):
    try:
        input_data = request.data
        alert_type, parent_category_id, our_category_name, store_id, product_id = '', '', '', '', ''

        try:
            if len(input_data) == 0:
                context = {'Message': "Error in Setting Alert, request body is empty.", "Status": False}
                return Response(context)
        except:
            context = {'Message': "Error in Setting Alert, request body is empty.", "Status": False}
            return Response(context)
        try:
            userid = int(input_data['userid'])
            if userid == False or userid == '' or not userid:
                context = {'Message': "Error in Setting Alert,userid id is empty.", "Status": False}
                return Response(context)
        except:
            context = {'Message': "Error in Setting Alert,userid id is invalid.", "Status": False}
            return Response(context)
        user_obj = Users.objects.filter(id=userid)
        if user_obj.exists() == False:
            context = {'Message': "Error in Setting Alert,User id not exists.", "Status": False}
            return Response(context)
        try:
            email_address = (input_data['email_address'])
            if email_address == False or email_address == '' or not email_address:
                context = {'Message': "Error in Setting Alert,email_address is empty.", "Status": False}
                return Response(context)
        except:
            context = {'Message': "Error in Setting Alert,email_address is invalid.", "Status": False}
            return Response(context)
        try:
            alert_nature = (input_data['alert_nature'])
            alert_nature = 'Weekly' if alert_nature == "False" or alert_nature == False or alert_nature == '0' or alert_nature == '' else alert_nature
        except:
            alert_nature = 'Weekly'
        try:
            name = (input_data['name'])
            name = '' if name == "False" or name == '0' or name == '' else name
        except:
            name = None
        try:
            product_id = int(input_data['product_id'])
            product_id = '' if product_id == "False" or product_id == False or product_id == '0' or product_id == '' else product_id
            product_obj = Products.objects.filter(id=product_id)
            if product_id and product_obj.exists() == False:
                context = {'Message': "Error in Setting Alert,Product id :" + str(product_id) + " not exists.",
                           "Status": False}
                return Response(context)
            else:
                product_id = product_obj[0]
                alert_type = "Product"
        except:
            product_id = None
        try:
            parent_category_name = (input_data['parent_category_name'])
            parent_category_name = '' if parent_category_name == "False" or parent_category_name == False or parent_category_name == '0' or parent_category_name == '' else parent_category_name
            parent_categories_obj = Parent_Categories.objects.filter(
                parent_category_name__iexact=parent_category_name.strip())
            if parent_category_name and parent_categories_obj.exists() == False:
                context = {'Message': "Error in Setting Alert,parent category name :" + str(
                    parent_category_name) + " not exists.", "Status": False}
                return Response(context)
            else:
                parent_category_id = parent_categories_obj[0].id
                alert_type = "Parent Category"
        except Exception as e:
            parent_category_id = None

        try:
            our_category_name = (input_data['our_category_name'])
            our_category_name = '' if our_category_name == "False" or our_category_name == False or our_category_name == '0' or our_category_name == '' else our_category_name
            our_category_name_obj = Our_Categories.objects.filter(category_name__iexact=our_category_name.strip())
            if our_category_name and our_category_name_obj.exists() == False:
                context = {'Message': "Error in Setting Alert,parent our category name :" + str(
                    our_category_name) + " not exists.", "Status": False}
                return Response(context)
            else:
                our_category_id = our_category_name_obj[0].id
                alert_type = "Our Category"
        except Exception as e:
            our_category_id = None
        try:
            store_name = (input_data['store_name'])
            store_name = '' if store_name == "False" or store_name == '0' or store_name == False or store_name == '' else store_name
            store_name_obj = Stores.objects.filter(store_name__iexact=store_name.strip())
            if store_name and store_name_obj.exists() == False:
                context = {
                    'Message': "Error in Setting Alert,parent our store  name :" + str(store_name) + " not exists.",
                    "Status": False}
                return Response(context)
            else:
                store_id = store_name_obj[0].id
                alert_type = "Store"
        except Exception as e:
            store_id = None
        if not parent_category_id and not our_category_id and not store_id and not product_id:
            context = {
                'Message': "Error in Setting Alert.product name,parent category name,our category name and store name are all empty.",
                "Status": False}
            return Response(context)
        if Email_Alerts.objects.filter(user_id=user_obj[0], product_id=product_id,
                                       parent_category_id=parent_category_id, our_category_id=our_category_id,
                                       store_id=store_id, name=name, email_address=email_address, alert_type=alert_type,
                                       alert_nature=alert_nature).exists() == True:
            context = {'Message': "Already set as Alert.", "Status": False}
            return Response(context)
        else:
            Email_Alerts(user_id=user_obj[0], product_id=product_id, parent_category_id=parent_category_id,
                         our_category_id=our_category_id, store_id=store_id, name=name, email_address=email_address,
                         alert_type=alert_type, alert_nature=alert_nature, created_at=timezone.now()).save()
        return Response({'Message': "Set as Alert.", "Status": True})
    except Exception as e:
        context = {'Message': 'Error in Setting Alert,check format of request body and try again.', "Status": False}
        ShowException(e)
        return Response(context)


@api_view(['GET', 'POST'])
@csrf_exempt
def RemoveProductAlert(request):
    try:
        input_data = request.data
        try:
            if len(input_data) == 0:
                context = {'Message': "Error in Removing Alert, request body is empty.", "Status": False}
                return Response(context)
        except:
            context = {'Message': "Error in Removing Alert, request body is empty.", "Status": False}
            return Response(context)
        try:
            userid = int(input_data['userid'])
            if userid == False or userid == '' or not userid:
                context = {'Message': "Error in Removing Alert,userid id is empty.", "Status": False}
                return Response(context)
        except:
            context = {'Message': "Error in Removing Alert,userid id is invalid.", "Status": False}
            return Response(context)
        user_obj = Users.objects.filter(id=userid)
        email_alerts_obj = False
        if user_obj.exists() == False:
            context = {'Message': "Error in Removing Alert,User id not exists.", "Status": False}
            return Response(context)
        try:
            product_id = int(input_data['product_id'])
            product_id = '' if product_id == "False" or product_id == '0' or product_id == '' else product_id
            product_obj = Products.objects.filter(id=product_id)
            if product_id and product_obj.exists() == False:
                context = {'Message': "Error in Setting Alert,Product id :" + str(product_id) + " not exists.",
                           "Status": False}
                return Response(context)
            else:
                product_id = product_obj[0]
                email_alerts_obj = Email_Alerts.objects.filter(user_id=user_obj[0], product_id=product_id)
        except:
            product_id = None
        try:
            parent_category_name = (input_data['parent_category_name'])
            parent_category_name = '' if parent_category_name == "False" or parent_category_name == '0' or parent_category_name == '' else parent_category_name
            parent_categories_obj = Parent_Categories.objects.filter(
                parent_category_name__iexact=parent_category_name.strip())
            if parent_category_name and parent_categories_obj.exists() == False:
                context = {'Message': "Error in Setting Alert,parent category name :" + str(
                    parent_category_name) + " not exists.", "Status": False}
                return Response(context)
            else:
                parent_category_id = parent_categories_obj[0].id
                email_alerts_obj = Email_Alerts.objects.filter(user_id=user_obj[0],
                                                               parent_category_id=parent_category_id)
        except Exception as e:
            parent_category_id = None

        try:
            our_category_name = (input_data['our_category_name'])
            our_category_name = '' if our_category_name == "False" or our_category_name == '0' or our_category_name == '' else our_category_name
            our_category_name_obj = Our_Categories.objects.filter(category_name__iexact=our_category_name.strip())
            if our_category_name and our_category_name_obj.exists() == False:
                context = {'Message': "Error in Setting Alert,parent our category name :" + str(
                    our_category_name) + " not exists.", "Status": False}
                return Response(context)
            else:
                our_category_id = our_category_name_obj[0].id
                email_alerts_obj = Email_Alerts.objects.filter(user_id=user_obj[0], our_category_id=our_category_id)
        except Exception as e:
            our_category_id = None
        try:
            store_name = (input_data['store_name'])
            store_name = '' if store_name == "False" or store_name == '0' or store_name == '' else store_name
            store_name_obj = Stores.objects.filter(store_name__iexact=store_name.strip())
            if store_name and store_name_obj.exists() == False:
                context = {
                    'Message': "Error in Setting Alert,parent our store  name :" + str(store_name) + " not exists.",
                    "Status": False}
                return Response(context)
            else:
                store_id = store_name_obj[0].id
                email_alerts_obj = Email_Alerts.objects.filter(user_id=user_obj[0], store_id=store_id)

        except Exception as e:
            store_id = None
        if not parent_category_id and not our_category_id and not store_id and not product_id:
            context = {
                'Message': "Error in Removing Alert.Keys product name,parent category name,our category name and store name are all empty.",
                "Status": False}
            return Response(context)
        if email_alerts_obj.exists() == True:
            email_alerts_obj.delete()
            context = {'Message': "Alert removed.", "Status": True}
            return Response(context)
        else:
            return Response({'Message': "Data to delete not found in alerts.", "Status": False})
    except Exception as e:
        context = {'Message': 'Error in Removing Alert,check format of request body and try again.', "Status": False}
        ShowException(e)
        return Response(context)


@api_view(['GET', 'POST'])
@csrf_exempt
def MarkProdcutFavoruite(request):
    try:
        input_data = request.data
        try:
            if len(input_data) == 0:
                context = {'Message': "Error in marking products as favourite, request body is empty.", "Status": False}
                return Response(context)
        except:
            context = {'Message': "Error in marking products as favourite, request body is empty.", "Status": False}
            return Response(context)
        try:
            product_id = int(input_data['products_id'])
            if product_id == False or product_id == '' or not product_id:
                context = {'Message': "Error in marking products as favourite,products id is empty.", "Status": False}
                return Response(context)
        except:
            context = {'Message': "Error in marking products as favourite,products id is invalid.", "Status": False}
            return Response(context)
        try:
            userid = int(input_data['userid'])
            if userid == False or userid == '' or not userid:
                context = {'Message': "Error in marking products as favourite,userid id is empty.", "Status": False}
                return Response(context)
        except:
            context = {'Message': "Error in marking products as favourite,userid id is invalid.", "Status": False}
            return Response(context)
        if Users.objects.filter(id=userid).exists() == False:
            context = {'Message': "User id not exists.", "Status": False}
            return Response(context)
        if Products.objects.filter(id=product_id).exists() == False:
            context = {'Message': "Product id not exists.", "Status": False}
            return Response(context)
        if Favourite_Ads.objects.filter(user_id=Users.objects.filter(id=userid)[0],
                                        product_id=Products.objects.filter(id=product_id)[0]).exists() == True:
            context = {'Message': "Already marked as favourite.", "Status": False}
            return Response(context)
        else:
            Favourite_Ads(user_id=Users.objects.filter(id=userid)[0],
                          product_id=Products.objects.filter(id=product_id)[0], created_at=timezone.now()).save()
        return Response({'Message': "Product marked as favourite.", "Status": True})
    except Exception as e:
        context = {
            'Message': 'Error in marking products as favourite,check format of request body,userid and product id and try again.',
            "Status": False}
        ShowException(e)
        return Response(context)


@api_view(['GET', 'POST'])
@csrf_exempt
def RemoveProdcutFromFavoruite(request):
    try:
        input_data = request.data
        try:
            if len(input_data) == 0:
                context = {'Message': "Error in removing products from favourite, request body is empty.",
                           "Status": False}
                return Response(context)
        except:
            context = {'Message': "Error in removing products from favourite, request body is empty.", "Status": False}
            return Response(context)
        try:
            product_id = int(input_data['product_id'])
            if product_id == False or product_id == '' or not product_id:
                context = {'Message': "Error in removing products from favourite,products id is empty.",
                           "Status": False}
                return Response(context)
        except:
            context = {'Message': "Error in removing products from favourite,products id is invalid.", "Status": False}
            return Response(context)
        try:
            userid = int(input_data['userid'])
            if userid == False or userid == '' or not userid:
                context = {'Message': "Error in removing products from favourite,userid id is empty.", "Status": False}
                return Response(context)
        except:
            context = {'Message': "Error in removing products from favourite,userid id is invalid.", "Status": False}
            return Response(context)
        if Users.objects.filter(id=userid).exists() == False:
            context = {'Message': "Error in removing products from favourite.User id not exists.", "Status": False}
            return Response(context)
        if Products.objects.filter(id=product_id).exists() == False:
            context = {'Message': "Error in removing products from favourite.Product id not exists.", "Status": False}
            return Response(context)
        favourite_obj = Favourite_Ads.objects.filter(user_id=Users.objects.filter(id=userid)[0],
                                                     product_id=Products.objects.filter(id=product_id)[0])
        if favourite_obj.exists() == True:
            favourite_obj.delete()
            context = {'Message': "Removed from favourite.", "Status": True}
            return Response(context)
        else:
            return Response({'Message': "User id:" + str(userid) + " and Product id:" + str(
                product_id) + " not found in favourite.", "Status": False})
    except Exception as e:
        context = {
            'Message': 'Error in removing products from favourite,check format of request body,userid and product id and try again.',
            "Status": False}
        ShowException(e)
        return Response(context)


@api_view(['GET', 'POST'])
@csrf_exempt
def GetSimilarProducts(request):
    try:
        input_data = request.data
        try:
            if len(input_data) == 0:
                context = {'Message': "Error in getting similar product, request body is empty.", "Status": False}
                return Response(context)
        except:
            context = {'Message': "Error in getting similar product, request body is empty.", "Status": False}
            return Response(context)
        try:
            product_id = int(input_data['product_id'])
            if product_id == False or product_id == '' or not product_id:
                context = {'Message': "Error in getting similar product,products id is empty.", "Status": False}
                return Response(context)
        except:
            context = {'Message': "Error in getting similar product,products id is invalid.", "Status": False}
            return Response(context)

            # scrapper_product_id,MachineName with this product_id=> then get GroupId with reference to this scrapper_product_id,MachineName from ProductSimilarity , then get ProductId from ProductSimilarity and fetch records of those ids from products table.
        products_obj = Products.objects.filter(id=product_id)
        if products_obj.exists() == False:
            context = {'Message': "Product id not exists.", "Status": False}
            return Response(context)
        product_list = []
        try:
            for row in ProductSimilarity.objects.filter(GroupId=ProductSimilarity.objects.filter(
                    ProductId=products_obj[0].scrapper_product_id, MachineName=products_obj[0].machinename)[0].GroupId,
                                                        MachineName=products_obj[0].machinename):
                product_color_sizes_list = []
                product_color_sizes_obj = Product_Color_Sizes.objects.filter(
                    product_id__scrapper_product_id=row.ProductId, product_id__machinename=products_obj[0].machinename)
                for s in product_color_sizes_obj:
                    product_color_sizes_list.append(
                        {"id": s.id, "product_id": s.product_id.id, "color_map_id": s.color_map_id,
                         "color_name": s.color_name, "size_map_id": s.size_map_id,
                         "size_type": s.size_type, "price": s.price, "sale_price": s.sale_price})
                if product_color_sizes_obj.exists():
                    product_list.append({
                        "id": product_color_sizes_obj[0].product_id.id,
                        "name": product_color_sizes_obj[0].product_id.name,
                        "all_images": product_color_sizes_obj[0].product_id.all_images,
                        "image": product_color_sizes_obj[0].product_id.image,
                        "product_color_sizes": product_color_sizes_list,
                        "petite_size": product_color_sizes_obj[0].product_id.petite_size,
                        "short_size": product_color_sizes_obj[0].product_id.short_size,
                        "long_size": product_color_sizes_obj[0].product_id.long_size,
                        "xlong_size": product_color_sizes_obj[0].product_id.xlong_size,
                        "plus_size": product_color_sizes_obj[0].product_id.plus_size,
                        "regular_size": product_color_sizes_obj[0].product_id.regular_size,
                        "tall_size": product_color_sizes_obj[0].product_id.tall_size,
                        "material": product_color_sizes_obj[0].product_id.material,
                        "feature": product_color_sizes_obj[0].product_id.feature,
                        "dress_length": product_color_sizes_obj[0].product_id.dress_length,
                        "characters": product_color_sizes_obj[0].product_id.characters,
                        "fit_type": product_color_sizes_obj[0].product_id.fit_type,
                        "closure": product_color_sizes_obj[0].product_id.closure,
                        "dress_style": product_color_sizes_obj[0].product_id.dress_style,
                        "pattern": product_color_sizes_obj[0].product_id.pattern,
                        "neckline": product_color_sizes_obj[0].product_id.neckline,
                        "theme": product_color_sizes_obj[0].product_id.theme,
                        "fastening_type": product_color_sizes_obj[0].product_id.fastening_type,
                        "collar": product_color_sizes_obj[0].product_id.collar,
                        "cuff_style": product_color_sizes_obj[0].product_id.cuff_style,
                        "sleeve_length": product_color_sizes_obj[0].product_id.sleeve_length,
                        "sleeve_type": product_color_sizes_obj[0].product_id.sleeve_type,
                        "embellishment": product_color_sizes_obj[0].product_id.embellishment,
                        "occasion": product_color_sizes_obj[0].product_id.occasion,
                        "garment_care": product_color_sizes_obj[0].product_id.garment_care,
                        "season": product_color_sizes_obj[0].product_id.season,
                        "description": product_color_sizes_obj[0].product_id.description,
                        "brand": product_color_sizes_obj[0].product_id.brand,
                        "brand_slug ": product_color_sizes_obj[0].product_id.brand_slug,
                        "currency": product_color_sizes_obj[0].product_id.currency,
                        "price": product_color_sizes_obj[0].product_id.price,
                        "price_highest": product_color_sizes_obj[0].product_id.price_highest,
                        "sale_price": product_color_sizes_obj[0].product_id.sale_price,
                        "sale_price_highest": product_color_sizes_obj[0].product_id.sale_price_highest,
                        "store_name": product_color_sizes_obj[0].product_id.store_name,
                        "store_url": product_color_sizes_obj[0].product_id.store_url,
                        "discount_percentage": product_color_sizes_obj[0].product_id.discount_percentage,
                        "discount_percentage_highest": product_color_sizes_obj[
                            0].product_id.discount_percentage_highest,
                        "offer_type": product_color_sizes_obj[0].product_id.offer_type,
                        "last_scrapper_update": product_color_sizes_obj[0].product_id.last_scrapper_update

                    })
            return Response({'Message': 'Success', 'Status': True, 'return_data': product_list})
        except:
            context = {'Message': 'No similar product found for this product.', "Status": False}
            return Response(context)


    except Exception as e:
        context = {
            'Message': 'Error in getting similar product,check format of request body,userid and product id and try again.',
            "Status": False}
        ShowException(e)
        return Response(context)


@api_view(['GET', 'POST'])
@csrf_exempt
def GetPriceHistory(request):
    try:
        input_data = request.data
        try:
            if len(input_data) == 0:
                context = {'Message': "Error in getting product price history, request body is empty.", "Status": False}
                return Response(context)
        except:
            context = {'Message': "Error in getting product price history, request body is empty.", "Status": False}
            return Response(context)
        try:
            product_id = int(input_data['product_id'])
            if product_id == False or product_id == '' or not product_id:
                context = {'Message': "Error in getting product price history,products id is empty.", "Status": False}
                return Response(context)
        except:
            context = {'Message': "Error in getting product price history,products id is invalid.", "Status": False}
            return Response(context)

        products_obj = Products.objects.filter(id=product_id)
        if products_obj.exists() == False:
            context = {'Message': "Product id not exists.", "Status": False}
            return Response(context)
        product_list, categories, price, sale_price, max_min_list, max_min_date = [], [], [], [], [], []
        price_history_obj = Price_Histories.objects.filter(product_id=products_obj[0]).order_by('-updated_at')[:14]
        for product in price_history_obj:
            categories.append(product.updated_at.strftime("%d %b"))
            price.append(product.price)
            sale_price.append(product.sale_price)
            if float(product.sale_price) > 0:
                max_min_list.append(product.sale_price)
                max_min_date.append(product.updated_at)
            else:
                max_min_list.append(product.price)
                max_min_date.append(product.updated_at)

        price_today = price_history_obj[0].sale_price if price_history_obj[0].sale_price > 0 else price_history_obj[
            0].price
        try:
            highest_price = max(max_min_list)
            lowest_price = min(max_min_list)
            highest_date = max_min_date[max_min_list.index(highest_price)]
            lowest_date = max_min_date[max_min_list.index(lowest_price)]
            highest_date = highest_date.strftime("%d %b")
            lowest_date = lowest_date.strftime("%d %b")

        except Exception as e:
            highest_price = None
            lowest_price = None
            highest_date = None
            lowest_date = None

        context = {
            "categories": categories,
            "data": {
                "price": price,
                "sale_price": sale_price,
                "highest_price": highest_price,
                "highest_date": highest_date,
                "price_today": price_today,
                "lowest_date": lowest_date,
                "lowest_price": lowest_price
            },
            "product_name": {"name": products_obj[0].name},
        }

        return Response({'Message': 'Success', 'Status': True, 'return_data': context})
    except Exception as e:
        context = {'Message': 'Error in getting product price history,check format of request body and try again.',
                   "Status": False}
        ShowException(e)
        return Response(context)


@api_view(['GET', 'POST'])
@csrf_exempt
def GetBusinessListing(request):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="Api",
        port=3306
    )
    cursor = connection.cursor()
    try:
        input_data = request.data
        criterion1, criterion2, criterion3, criterion_gender = Q(), Q(), Q(), Q()
        limit_per_page, extra_query, extra_query2, extra_query3, extra_query_gender = '', '', '', '', ''

        try:
            if len(input_data) == 0:
                error = "Error in getting data, request body is empty."
                context = {'Message': error, 'return_data': []}
                return Response(context)
        except:
            error = "Error in getting data, request body is empty."
            context = {'Message': error, 'return_data': []}
            return Response(context)
        try:
            page = int(input_data['page'])
            page = 1 if page == 0 else page
        except:
            page = 1
        try:
            business_per_page = int(input_data['business_per_page'])
        except:
            business_per_page = 40
        try:
            user_timezone = (input_data['user_timezone'])
        except:
            user_timezone = False
        try:
            user_latitude = (input_data['user_latitude'])
        except:
            user_latitude = False
        try:
            user_longitude = (input_data['user_longitude'])
        except:
            user_longitude = False
        try:
            is_open_only = (input_data['is_open_only'])

        except:
            is_open_only = False
        try:
            is_open_next = (input_data['is_open_next'])
        except:
            is_open_next = False
        try:
            is_open_prev = (input_data['is_open_prev'])
        except:
            is_open_prev = False
        try:
            last_id = int(input_data['last_id'])
            if page == 1:
                last_id = 1
        except Exception as e:
            last_id = 1
        try:
            name_search = (input_data['name_search'])
        except:
            name_search = False
        try:
            address_search = (input_data['address_search'])
        except:
            address_search = False
        try:
            gender_search = (input_data['gender_search'])
            gender_search = [] if gender_search == False or gender_search == 0 or gender_search == '' else gender_search
            if 'women' in gender_search.lower():
                gender_search = ['women', 'bridal', 'boutique', 'clothing store']
            elif 'men' in gender_search.lower():
                gender_search = ['men', 'sportswear']
            else:
                gender_search = [gender_search]
            criterion_gender = Q(reduce(operator.or_, (Q(group_gender__icontains=str(x)) for x in
                                                       gender_search))) if gender_search else Q()
            extra_query_gender = extra_query_gender + " AND (%s)" % (
                ' OR '.join(' LOWER(group_gender) LIKE LOWER("%' + str(txt) + '%") ' for txt in gender_search))

        except Exception as e:
            gender_search = False

        endlimit = page * business_per_page
        start_limit = endlimit - business_per_page
        total_businesses = []
        if name_search:
            extra_query = ' AND (name LIKE "%' + str(name_search) + '%"   )'
            criterion1 = Q(name__icontains=name_search) if name_search else Q()

        if address_search:
            extra_query2 = ' AND ( city LIKE "%' + str(address_search) + '%" OR state LIKE "%' + str(
                address_search) + '%" OR zip_code LIKE "%' + str(address_search) + '%"  ) '
            criterion2 = Q(city__icontains=address_search) | Q(state__icontains=address_search) | Q(
                zip_code__icontains=address_search) if address_search else Q()

        if is_open_only:
            if is_open_prev and last_id == 1:
                extra_query3 = ' AND id>1'
                criterion3 = Q(id__gt=last_id)
            elif is_open_prev and (last_id != 1 or last_id != 0 or last_id != False or last_id != ''):
                extra_query3 = ' AND id<' + str(last_id)
                criterion3 = Q(id__lt=last_id)
            elif is_open_next:
                extra_query3 = ' AND id>' + str(last_id)
                criterion3 = Q(id__gt=last_id)
            else:
                pass

            limit_per_page = ''
        else:
            limit_per_page = '''LIMIT ''' + str(start_limit) + ''',''' + str(business_per_page)
        cursor.execute('''SELECT `Id`, `name`,`street_address`, `zip_code`,`years_in_business`, `city`, `state`, `country`,`phone`, `email`,
        `website`, `latitude`, `longitude`,`rating`, `store_url`, `time_zone`, `opening_closing`, `opening_closing_hours_meta`, `off_days`, `opening_closing_change`,
        (ST_Distance_Sphere(
            point(longitude, latitude),
            point(''' + str(user_longitude) + ''', ''' + str(user_latitude) + ''')
        ) * .000621371192) as Distance
        FROM `businesses`  WHERE (time_zone!="" or time_zone !=NULL) AND (opening_closing_hours_meta!="") AND  opening_closing_hours_meta NOT  LIKE "%x%" ''' + str(
            extra_query) + str(extra_query2) + str(extra_query3) + str(
            extra_query_gender) + ''' ORDER BY Distance ASC ''' + limit_per_page + '''; ''')

        print('''SELECT `Id`, `name`,`street_address`, `zip_code`,`years_in_business`, `city`, `state`, `country`,`phone`, `email`,
        `website`, `latitude`, `longitude`,`rating`, `store_url`, `time_zone`, `opening_closing`, `opening_closing_hours_meta`, `off_days`, `opening_closing_change`,
        (ST_Distance_Sphere(
            point(longitude, latitude),
            point(''' + str(user_longitude) + ''', ''' + str(user_latitude) + ''')
        ) * .000621371192) as Distance
        FROM `businesses`  WHERE (time_zone!="" or time_zone !=NULL) AND (opening_closing_hours_meta!="") AND  opening_closing_hours_meta NOT  LIKE "%x%" ''' + str(
            extra_query) + str(extra_query2) + str(extra_query3) + str(
            extra_query_gender) + ''' ORDER BY Distance ASC ''' + limit_per_page + '''; ''')

        total_businesses = Businesses.objects.filter(criterion1, criterion2, criterion3, criterion_gender).exclude(
            Q(time_zone='') | Q(time_zone__exact=None)).exclude(
            Q(opening_closing_hours_meta='') | Q(opening_closing_hours_meta__exact=None)).count()
        return_data = []
        tz = pytz.timezone(user_timezone)
        user_timezone_now = datetime.datetime.now(tz)
        for row in cursor.fetchall():
            last_id = row[0]
            is_open = False
            opening_today = False
            closing_today = False
            is_holiday = False
            time_zone = pytz.timezone(row[15])
            business_timezone_now = datetime.datetime.now(time_zone)
            opening_closing = row[16]
            opening_closing_hours_meta = row[17]
            off_days = row[18]
            opening_closing_change = row[19]

            # opening_closing_change= [{"2/01 to 3/19": [{"title": "Sun", "duration": "10:00am-08:00pm"}, {"title": "Mon", "duration": "10:00am-08:00pm"}, {"title": "Tue", "duration": "12:00am-11:59pm"}, {"title": "Wed", "duration": "Closed"}, {"title": "Thu", "duration": "10:00am-08:00pm"}, {"title": "Fri", "duration": "09:00am-09:00pm"}, {"title": "Sat", "duration": "09:00am-09:00pm"}]}, {" 12/20 to 12/23": [{"title": "Mon", "duration": "09:00am-09:00pm"}, {"title": "Tue", "duration": "09:00am-09:00pm"}, {"title": "Wed", "duration": "09:00am-09:00pm"}, {"title": "Thu", "duration": "09:00am-09:00pm"}, {"title": "Fri", "duration": "09:00am-09:00pm"}, {"title": "Sat", "duration": "09:00am-09:00pm"}, {"title": "Sun", "duration": "09:00am-09:00pm"}]}, {" 12/27 to 12/30": [{"title": "Mon", "duration": "11:00am-08:00pm"}, {"title": "Tue", "duration": "11:00am-08:00pm"}, {"title": "Wed", "duration": "11:00am-08:00pm"}, {"title": "Thu", "duration": "11:00am-08:00pm"}, {"title": "Fri", "duration": "11:00am-08:00pm"}, {"title": "Sat", "duration": "11:00am-08:00pm"}, {"title": "Sun", "duration": "11:00am-08:00pm"}]}]
            is_open, is_holiday, opening_today, closing_today = GetOpenCloseMain(opening_closing_change,
                                                                                 opening_closing_hours_meta, time_zone,
                                                                                 business_timezone_now,
                                                                                 user_timezone_now, tz)

            # if opening_closing_change:
            # for open_close in opening_closing_change:
            # for key, value in open_close.items():
            # date_year=key.split(' to ')
            # datetime_object1 = datetime.datetime.strptime(str(business_timezone_now.year)+'/'+date_year[0].strip()+" 00:00:00", '%Y/%m/%d %H:%M:%S')
            # datetime_object2 = datetime.datetime.strptime(str(business_timezone_now.year)+'/'+date_year[1].strip()+" 23:59:59", '%Y/%m/%d %H:%M:%S')
            ##Time With Businesses Timezone
            # datetime_object1 =ConvertTimeToBusinessTimezone(datetime_object1,time_zone)
            # datetime_object2 =ConvertTimeToBusinessTimezone(datetime_object2,time_zone)
            # if datetime_object1 <= business_timezone_now <= datetime_object2:
            # is_open,is_holiday,opening_today,closing_today=GetOpenClose(value,time_zone,business_timezone_now,user_timezone_now,tz)

            # elif opening_closing_hours_meta:
            # try:
            # json_list=json.loads(opening_closing_hours_meta)
            # json.dumps(json_list)
            # is_open,is_holiday,opening_today,closing_today=GetOpenClose(json_list,time_zone,business_timezone_now,user_timezone_now,tz)
            # except:
            # continue
            # else:
            # print("No condition matched.")

            if is_open_only == False or (is_open_only != False and is_open == True):
                return_data.append([
                    {
                        "id": row[0],
                        "name": row[1],
                        "street_address": row[2],
                        "zip_code": row[3],
                        "years_in_business": row[4],
                        "city": row[5],
                        "state": row[6],
                        "country": row[7],
                        "phone": row[8],
                        "email": row[9],
                        "website": row[10],
                        "latitude": row[11],
                        "longitude": row[12],
                        "rating": row[13],
                        "store_url": row[14],
                        "distance": row[20],
                        "is_open": is_open,
                        "opening_today": opening_today,
                        "closing_today": closing_today,
                        "is_holiday": is_holiday,
                    }])

            if len(return_data) == business_per_page:
                break

        cursor.close()
        return Response({'Message': 'Success', 'Status': True, 'page': page, 'TotalBusiness': total_businesses,
                         'FetchedBusiness': len(return_data), 'return_data': return_data, 'last_id': last_id})
    except Exception as e:
        context = {'Message': 'Error in getting businesses listing,check format of request body and try again.',
                   "Status": False}
        ShowException(e)
        return Response(context)


@api_view(['GET', 'POST'])
@csrf_exempt
def GetBusinessDetails(request):
    try:
        input_data = request.data
        try:
            if len(input_data) == 0:
                error = "Error in getting data, request body is empty."
                context = {'Message': error, 'return_data': []}
                return Response(context)
        except:
            error = "Error in getting data, request body is empty."
            context = {'Message': error, 'return_data': []}
            return Response(context)

        try:
            user_timezone = (input_data['user_timezone'])
        except:
            user_timezone = False
        try:
            user_latitude = (input_data['user_latitude'])
        except:
            user_latitude = False
        try:
            user_longitude = (input_data['user_longitude'])
        except:
            user_longitude = False
        try:
            business_id = int(input_data['business_id'])
        except:
            context = {'Message': 'Error in getting businesses details,Business id is Null.', "Status": False}
            return Response(context)

        distance = False
        if user_latitude and user_longitude:
            cursor.execute('''SELECT (ST_Distance_Sphere(
              point(longitude, latitude),
              point(''' + str(user_longitude) + ''', ''' + str(user_latitude) + ''')
          ) * .000621371192) as Distance  FROM businesses WHERE businesses.id=''' + str(business_id) + ''' ;''')
            for row in cursor.fetchall():
                distance = row[0]
        return_data = []
        tz = pytz.timezone(user_timezone)
        user_timezone_now = datetime.datetime.now(tz)
        return_data = []
        tz = pytz.timezone(user_timezone)
        user_timezone_now = datetime.datetime.now(tz)
        is_open, opening_today, closing_today, is_holiday = False, False, False, False
        businesses_obj = Businesses.objects.get(id=business_id)
        if not businesses_obj:
            context = {'Message': 'Error in getting businesses details,business_id not found with any record.',
                       "Status": False}
            return Response(context)
        time_zone = pytz.timezone(businesses_obj.time_zone)
        business_timezone_now = datetime.datetime.now(time_zone)
        opening_closing = businesses_obj.opening_closing
        opening_closing_hours_meta = businesses_obj.opening_closing_hours_meta
        off_days = businesses_obj.off_days
        opening_closing_change = businesses_obj.opening_closing_change
        is_open, is_holiday, opening_today, closing_today = GetOpenCloseMain(opening_closing_change,
                                                                             opening_closing_hours_meta, time_zone,
                                                                             business_timezone_now, user_timezone_now,
                                                                             tz)

        try:
            Business_Reviews_obj = Business_Reviews.objects.filter(business_id=businesses_obj)[0]
            if Business_Reviews_obj:
                Business_Reviews_data = [{
                    "user_id": Business_Reviews_obj.user_id.id,
                    "first_name": Business_Reviews_obj.user_id.first_name,
                    "last_name": Business_Reviews_obj.user_id.last_name,
                    "rating": Business_Reviews_obj.rating,
                    "rating_text": Business_Reviews_obj.rating_text,
                    "review_title": Business_Reviews_obj.review_title,
                    "review_text": Business_Reviews_obj.review_text,
                    "review_images": Business_Reviews_obj.review_images,
                    "parent_id": Business_Reviews_obj.parent_id,
                    "status": Business_Reviews_obj.status,
                    "created_at": Business_Reviews_obj.created_at,
                    "updated_at": Business_Reviews_obj.updated_at
                }]
            else:
                Business_Reviews_data = []
        except:
            Business_Reviews_data = []

        return_data = {
            "id": businesses_obj.id,
            "name": businesses_obj.name,
            "categories": businesses_obj.categories,
            "street_address": businesses_obj.street_address,
            "city": businesses_obj.city,
            "state": businesses_obj.state,
            "zip_code": businesses_obj.zip_code,
            "rating": businesses_obj.rating,
            "phone": businesses_obj.phone,
            "email": businesses_obj.email,
            "website": businesses_obj.website,
            "images": businesses_obj.years_in_business,
            "latitude": businesses_obj.latitude,
            "longitude": businesses_obj.longitude,
            "description": businesses_obj.description,
            "years_in_business": businesses_obj.years_in_business,
            "opening_closing": businesses_obj.opening_closing,
            "off_days": businesses_obj.off_days,
            "payment_methods": businesses_obj.payment_methods,
            "social_links": businesses_obj.social_links,
            "store_service_reviews": Business_Reviews_data,
            "country": businesses_obj.country,
            "store_url": businesses_obj.store_url,
            "distance": distance,
            "is_open": is_open,
            "opening_today": opening_today,
            "closing_today": closing_today,
            "is_holiday": is_holiday,
        }

        return Response({'Message': 'Success', 'Status': True, 'return_data': return_data})

    except Exception as e:
        context = {'Message': 'Error in getting businesses listing,check format of request body and try again.',
                   "Status": False}
        ShowException(e)
        return Response(context)


@api_view(['GET', 'POST'])
@csrf_exempt
def SaveReview(request):
    try:
        input_data = request.data
        try:
            if len(input_data) == 0:
                error = "Error in saving review, request body is empty."
                context = {'Message': error, 'return_data': []}
                return Response(context)
        except:
            error = "Error in saving review, request body is empty."
            context = {'Message': error, 'return_data': []}
            return Response(context)

        try:
            userid = int(input_data['userid'])
            user_obj = Users.objects.filter(id=userid)
            if user_obj.exists() == False:
                context = {'Message': "Error in saving review,User id not exists.", "Status": False}
                return Response(context)
        except:
            context = {'Message': 'Error in saving review,User id is Null.', "Status": False}
            return Response(context)

        try:
            business_id = int(input_data['business_id'])
            business_obj = Businesses.objects.filter(id=business_id)
            if business_obj.exists() == False:
                context = {'Message': "Error in saving review,Business id not exists.", "Status": False}
                return Response(context)
        except:
            context = {'Message': 'Error in saving review,Business id is Null.', "Status": False}
            return Response(context)

        try:
            rating = (input_data['rating'])
        except:
            rating = None
        try:
            rating_text = (input_data['rating_text'])
        except:
            rating_text = None
        try:
            review_title = (input_data['review_title'])
        except:
            review_title = None
        try:
            review_text = (input_data['review_text'])
        except:
            review_text = None
        try:
            review_images = (input_data['review_images'])
        except:
            review_images = None
        try:
            parent_id = (input_data['parent_id'])
            parent_id = None if (parent_id == False or parent_id == 0 or parent_id == '') else parent_id
            if parent_id:
                parent_id_obj = Business_Reviews.objects.filter(id=parent_id)
                if parent_id_obj.exists() == False:
                    context = {'Message': "Error in saving review,Parent id not exists.", "Status": False}
                    return Response(context)
        except:
            parent_id = None
        try:
            Business_Reviews(business_id=business_obj[0], user_id=user_obj[0], rating=rating, rating_text=rating_text,
                             review_title=review_title, review_text=review_text,
                             review_images=review_images, parent_id=parent_id, status='Active',
                             created_at=datetime.datetime.now(), updated_at=datetime.datetime.now()).save()

            UpdateRating(business_obj[0])
            return Response({'Message': 'Success', 'Status': True, })
        except Exception as e:
            return Response({'Message': 'Error in saving review.' + str(e), 'Status': False})


    except Exception as e:
        context = {'Message': 'Error in saving review,check format of request body and try again.', "Status": False}
        ShowException(e)
        return Response(context)


@api_view(['GET', 'POST'])
@csrf_exempt
def UpdateReview(request):
    try:
        input_data = request.data
        try:
            if len(input_data) == 0:
                error = "Error in updating review, request body is empty."
                context = {'Message': error, 'return_data': []}
                return Response(context)
        except:
            error = "Error in updating review, request body is empty."
            context = {'Message': error, 'return_data': []}
            return Response(context)

        try:
            userid = int(input_data['userid'])
            user_obj = Users.objects.filter(id=userid)
            if user_obj.exists() == False:
                context = {'Message': "Error in updating review,User id not exists.", "Status": False}
                return Response(context)
        except:
            context = {'Message': 'Error in updating review,User id is Null.', "Status": False}
            return Response(context)

        try:
            review_id = int(input_data['review_id'])
            business_reviews_obj = Business_Reviews.objects.filter(id=review_id, user_id=user_obj[0])
            if business_reviews_obj.exists() == False:
                context = {'Message': "Error in updating review,Review id not exists with current user.",
                           "Status": False}
                return Response(context)
        except:
            context = {'Message': 'Error in updating review,Review id is Null.', "Status": False}
            return Response(context)

        try:
            rating = (input_data['rating'])
        except:
            rating = None
        try:
            rating_text = (input_data['rating_text'])
        except:
            rating_text = None
        try:
            review_title = (input_data['review_title'])
        except:
            review_title = None
        try:
            review_text = (input_data['review_text'])
        except:
            review_text = None
        try:
            review_images = (input_data['review_images'])
        except:
            review_images = None
        try:
            status = (input_data['status'])
        except:
            status = "Active"
        try:
            parent_id = (input_data['parent_id'])
            parent_id = None if (parent_id == False or parent_id == 0 or parent_id == '') else parent_id
            if parent_id:
                parent_id_obj = Business_Reviews.objects.filter(id=parent_id)
                if parent_id_obj.exists() == False:
                    context = {'Message': "Error in updating review,Parent id not exists.", "Status": False}
                    return Response(context)
        except:
            parent_id = None
        try:
            business_reviews_obj.update(parent_id=parent_id, rating=rating, rating_text=rating_text,
                                        review_title=review_title, review_text=review_text, review_images=review_images,
                                        status=status, updated_at=datetime.datetime.now())
            UpdateRating(business_reviews_obj[0].business_id)
            return Response({'Message': 'Success', 'Status': True})
        except Exception as e:
            return Response({'Message': 'Error in updating review.' + str(e), 'Status': False})


    except Exception as e:
        context = {'Message': 'Error in updating review,check format of request body and try again.', "Status": False}
        ShowException(e)
        return Response(context)


@api_view(['GET', 'POST'])
@csrf_exempt
def DeleteReview(request):
    try:
        input_data = request.data
        try:
            if len(input_data) == 0:
                error = "Error in deleting review, request body is empty."
                context = {'Message': error, 'return_data': []}
                return Response(context)
        except:
            error = "Error in deleting review, request body is empty."
            context = {'Message': error, 'return_data': []}
            return Response(context)

        try:
            userid = int(input_data['userid'])
            user_obj = Users.objects.filter(id=userid)
            if user_obj.exists() == False:
                context = {'Message': "Error in deleting review,User id not exists.", "Status": False}
                return Response(context)
        except:
            context = {'Message': 'Error in deleting review,User id is Null.', "Status": False}
            return Response(context)

        try:
            review_id = int(input_data['review_id'])
            business_reviews_obj = Business_Reviews.objects.filter(id=review_id, user_id=user_obj[0])
            if business_reviews_obj.exists() == False:
                context = {'Message': "Error in deleting review,Review id not exists with current user.",
                           "Status": False}
                return Response(context)
            else:
                try:
                    Business_Reviews.objects.filter(parent_id=business_reviews_obj[0].id).delete()
                    business_id = business_reviews_obj[0].business_id
                    business_reviews_obj.delete()
                    UpdateRating(business_id)
                    return Response({'Message': 'Success', 'Status': True})
                except Exception as e:
                    return Response({'Message': 'Error in deleting review.' + str(e), 'Status': False})

        except:
            context = {'Message': 'Error in deleting review,Review id is Null.', "Status": False}
            return Response(context)
    except Exception as e:
        context = {'Message': 'Error in deleting review,check format of request body and try again.', "Status": False}
        ShowException(e)
        return Response(context)
