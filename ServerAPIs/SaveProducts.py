import datetime
import json
import re
import sys, os, operator
import traceback

import unidecode as unidecode
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from ServerAPIs.models import *
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from functools import reduce
from django.db import connection
from py_linq import Enumerable
from django.db.models import Q


@api_view(['POST'])
@csrf_exempt
def save_products(request):
    try:
        productJson = json.loads(json.dumps(request.data))
    except Exception as e:
        ex = ShowException(e)
        context = {'Error': 'Error getting product data: ' + str(ex), 'return_data': []}
        return Response(context)

    saved = 0
    failed = 0
    for productToken in productJson:
        themes = []
        seasons = []
        collars = []
        patterns = []
        features = []
        closures = []
        fit_types = []
        occasions = []
        necklines = []
        materials = []
        tall_sizes = []
        plus_sizes = []
        short_sizes = []
        long_sizes = []
        x_long_sizes = []
        characters = []
        color_names = []
        cuff_styles = []
        sleeve_types = []
        dress_styles = []
        petite_sizes = []
        size_map_list = []
        regular_sizes = []
        dress_lengths = []
        garment_cares = []
        material_names = []
        sleeve_lengths = []
        embellishments = []
        fastening_types = []
        product_col_sizes = []
        promo_offer_types = []
        promo_offer_labels = []
        price_offer_types = []
        price_offer_labels = []
        ship_offer_types = []
        ship_offer_labels = []
        other_offer_types = []
        other_offer_labels = []
        promos_dict = {}
        try:
            scrapper_result_id = productToken['scrapper_result_id']
            scrapper_product_id = productToken['scrapper_product_id']
            name = productToken['name']
            product_slug = Slugify(name)
            price = productToken['price']
            sale_price = productToken['sale_price']
            price_lowest = float(productToken['price_lowest'])
            sale_price_lowest = float(productToken['sale_price_lowest'])
            if price_lowest != 0.0:
                price = price_lowest
                sale_price = sale_price_lowest
            price_highest = productToken['price_highest']
            sale_price_highest = productToken['sale_price_highest']

            discount_percentage = productToken['discount_percentage']
            if "-" in discount_percentage:
                percentage = discount_percentage.split('-')
                discount_percentage = percentage[0]
                discount_percentage_highest = percentage[1]
            else:
                discount_percentage_highest = ''

            parent_category_ids = list(productToken['parent_category_id'].split(','))
            if len(parent_category_ids) > 1:
                parent_category_id = int(parent_category_ids[0])
                parent_category_name = Parent_Categories.objects.get(id=parent_category_id).parent_category_name
                parent_category_id_2 = int(parent_category_ids[1])
                parent_category_name_2 = Parent_Categories.objects.get(id=parent_category_id_2).parent_category_name
            else:
                parent_category_id = int(parent_category_ids[0])
                parent_category_name = Parent_Categories.objects.get(id=parent_category_id).parent_category_name
                parent_category_id_2 = None
                parent_category_name_2 = None

            category_ids = list(productToken['category_id'].split(','))
            if len(category_ids) > 1:
                our_category_id = int(category_ids[0])
                our_category_name = Our_Categories.objects.get(parent_category_id=parent_category_id,
                                                               id=our_category_id).category_name
                our_category_id_2 = int(category_ids[1])
                our_category_name_2 = Our_Categories.objects.get(parent_category_id=parent_category_id,
                                                                 id=our_category_id_2).category_name
            else:
                our_category_id = int(category_ids[0])
                our_category_name = Our_Categories.objects.get(parent_category_id=parent_category_id,
                                                               id=our_category_id).category_name
                our_category_id_2 = None
                our_category_name_2 = None

            store_id = int(productToken['store_id'])
            store_name = Stores.objects.get(id=store_id).store_name
            store_logo = Stores.objects.get(id=store_id).store_logo
            store_url = Stores.objects.get(id=store_id).store_url

            brand = productToken['brand']
            if not Stores.objects.filter(nature='Brand', store_name=brand).exists():
                newStore = Stores.objects.create(store_name=brand, store_url=store_url, nature='Brand')
                storeSlug = Slugify(brand) + "-" + str(newStore.id)
                Stores.objects.filter(id=newStore.id).update(store_slug=storeSlug)

            brand_id = Stores.objects.get(nature='Brand', store_name=brand).id
            brand_slug = Stores.objects.get(nature='Brand', store_name=brand).store_slug

            for color_token in productToken['color_id']:
                color_map_id = color_token['id']
                color_price = color_token['price']
                color_name = color_token['color_name']
                color_names.append(color_name)
                for size_token in color_token['sizes']:
                    size_map_id = size_token['our_size']
                    size_price = size_token['price']
                    size_sale_price = size_token['sale_price']

                    size_type = size_token['size_type']
                    if 'Petite' in size_type:
                        petite_sizes.append(size_map_id)
                    elif 'Plus' in size_type:
                        plus_sizes.append(size_map_id)
                    elif 'Tall' in size_type:
                        tall_sizes.append(size_map_id)
                    elif 'Short' in size_type:
                        short_sizes.append(size_map_id)
                    elif 'Long' in size_type:
                        long_sizes.append(size_map_id)
                    elif 'Extra Long' in size_type:
                        x_long_sizes.append(size_map_id)
                    else:
                        regular_sizes.append(size_map_id)

                    product_col_sizes.append(
                        (scrapper_product_id, color_map_id, color_name, color_price, size_map_id, size_type, size_price,
                         size_sale_price))

            color = " | ".join(color_names)

            for size_token in productToken['size']:
                our_size = size_token['our_size']
                if our_size == '':
                    our_size = 'Not Specified'
                our_size_slug = Slugify(our_size)
                size_type = size_token['size_type']
                size_name = size_token['size_name']
                size_map_slug = Slugify(size_type + " " + size_name)
                size_map_list.append((our_size, our_size_slug, size_type, size_name, size_map_slug))

            for promo_offer_type in productToken['promo_offer_type']:
                promo_offer_types.append(Our_Filters.objects.get(filter_type='offer_type',
                                                                 id=int(promo_offer_type['id'])).filter_name)
                promo_offer_labels.append(promo_offer_type['offer_type_label'])

            for price_offer_type in productToken['price_offer_type']:
                price_offer_types.append(Our_Filters.objects.get(filter_type='offer_type',
                                                                 id=int(price_offer_type['id'])).filter_name)
                price_offer_labels.append(price_offer_type['offer_type_label'])

            for ship_offer_type in productToken['shipping_offer_type']:
                ship_offer_types.append(
                    Our_Filters.objects.get(filter_type='offer_type', id=int(ship_offer_type['id'])).filter_name)
                ship_offer_labels.append(ship_offer_type['offer_type_label'])

            for other_offer_type in productToken['other_offer_type']:
                other_offer_types.append(Our_Filters.objects.get(filter_type='offer_type',
                                                                 id=int(other_offer_type['id'])).filter_name)
                other_offer_labels.append(other_offer_type['offer_type_label'])
            for materialID in productToken['material'].split(','):
                material_names.append(
                    Our_Filters.objects.get(
                        (Q(parent_category_id=parent_category_id) | Q(parent_category_id=parent_category_id_2)),
                        filter_type='material', id=int(materialID)).filter_name)

            materialList = [
                list(map(lambda orig_string: orig_string + "%", productToken['material_percentage'].split(','))),
                material_names]

            materialList = list(map(" ".join, zip(*materialList)))
            for material in materialList:
                if material.strip().startswith('0%'):
                    material = material.replace('0%', '').strip()
                materials.append(material)

            if productToken['fit_type'] != '':
                for fit_type in productToken['fit_type'].split(','):
                    fit_types.append(
                        Our_Filters.objects.get(
                            (Q(parent_category_id=parent_category_id) | Q(parent_category_id=parent_category_id_2)),
                            filter_type='fit_type', id=int(fit_type)).filter_name)

            if productToken['characters'] != '':
                for character in productToken['characters'].split(','):
                    characters.append(
                        Our_Filters.objects.get(
                            (Q(parent_category_id=parent_category_id) | Q(parent_category_id=parent_category_id_2)),
                            filter_type='character', id=int(character)).filter_name)

            if productToken['closures'] != '':
                for closure in productToken['closures'].split(','):
                    closures.append(
                        Our_Filters.objects.get(
                            (Q(parent_category_id=parent_category_id) | Q(parent_category_id=parent_category_id_2)),
                            filter_type='closure', id=int(closure)).filter_name)

            if productToken['dress_lengths'] != '':
                for dress_length in productToken['dress_lengths'].split(','):
                    dress_lengths.append(
                        Our_Filters.objects.get(
                            (Q(parent_category_id=parent_category_id) | Q(parent_category_id=parent_category_id_2)),
                            filter_type='dress_length', id=int(dress_length)).filter_name)

            if productToken['dress_styles'] != '':
                for dress_style in productToken['dress_styles'].split(','):
                    dress_styles.append(
                        Our_Filters.objects.get(
                            (Q(parent_category_id=parent_category_id) | Q(parent_category_id=parent_category_id_2)),
                            filter_type='dress_style', id=int(dress_style)).filter_name)

            if productToken['embellishments'] != '':
                for embellishment in productToken['embellishments'].split(','):
                    embellishments.append(
                        Our_Filters.objects.get(
                            (Q(parent_category_id=parent_category_id) | Q(parent_category_id=parent_category_id_2)),
                            filter_type='embellishment', id=int(embellishment)).filter_name)

            if productToken['features'] != '':
                for feature in productToken['features'].split(','):
                    features.append(
                        Our_Filters.objects.get(
                            (Q(parent_category_id=parent_category_id) | Q(parent_category_id=parent_category_id_2)),
                            filter_type='feature', id=int(feature)).filter_name)

            if productToken['seasons'] != '':
                for season in productToken['seasons'].split(','):
                    seasons.append(Our_Filters.objects.get(filter_type='season', id=int(season)).filter_name)

            if productToken['garment_cares'] != '':
                for garment_care in productToken['garment_cares'].split(','):
                    garment_cares.append(
                        Our_Filters.objects.get(filter_type='garment_care', id=int(garment_care)).filter_name)

            if productToken['patterns'] != '':
                for pattern in productToken['patterns'].split(','):
                    patterns.append(
                        Our_Filters.objects.get(
                            (Q(parent_category_id=parent_category_id) | Q(parent_category_id=parent_category_id_2)),
                            filter_type='pattern', id=int(pattern)).filter_name)

            if productToken['necklines'] != '':
                for neckline in productToken['necklines'].split(','):
                    necklines.append(
                        Our_Filters.objects.get(
                            (Q(parent_category_id=parent_category_id) | Q(parent_category_id=parent_category_id_2)),
                            filter_type='neckline', id=int(neckline)).filter_name)

            if productToken['characters'] != '':
                for occasion in productToken['occasions'].split(','):
                    occasions.append(
                        Our_Filters.objects.get(
                            (Q(parent_category_id=parent_category_id) | Q(parent_category_id=parent_category_id_2)),
                            filter_type='occasion', id=int(occasion)).filter_name)

            if productToken['sleeve_lengths'] != '':
                for sleeve_length in productToken['sleeve_lengths'].split(','):
                    sleeve_lengths.append(
                        Our_Filters.objects.get(
                            (Q(parent_category_id=parent_category_id) | Q(parent_category_id=parent_category_id_2)),
                            filter_type='sleeve_length', id=int(sleeve_length)).filter_name)

            if productToken['sleeve_types'] != '':
                for sleeve_type in productToken['sleeve_types'].split(','):
                    sleeve_types.append(
                        Our_Filters.objects.get(
                            (Q(parent_category_id=parent_category_id) | Q(parent_category_id=parent_category_id_2)),
                            filter_type='sleeve_type', id=int(sleeve_type)).filter_name)

            if productToken['themes'] != '':
                for theme in productToken['themes'].split(','):
                    themes.append(Our_Filters.objects.get(
                        (Q(parent_category_id=parent_category_id) | Q(parent_category_id=parent_category_id_2)),
                        filter_type='theme', id=int(theme)).filter_name)

            if productToken['fastening_type'] != '':
                for fastening_type in productToken['fastening_type'].split(','):
                    fastening_types.append(
                        Our_Filters.objects.get(
                            (Q(parent_category_id=parent_category_id) | Q(parent_category_id=parent_category_id_2)),
                            filter_type='fastening_type', id=int(fastening_type)).filter_name)

            if productToken['cuff_styles'] != '':
                for cuff_style in productToken['cuff_styles'].split(','):
                    cuff_styles.append(
                        Our_Filters.objects.get(
                            (Q(parent_category_id=parent_category_id) | Q(parent_category_id=parent_category_id_2)),
                            filter_type='cuff_style', id=int(cuff_style)).filter_name)

            if productToken['collars'] != '':
                for collar in productToken['collars'].split(','):
                    collars.append(Our_Filters.objects.get(
                        (Q(parent_category_id=parent_category_id) | Q(parent_category_id=parent_category_id_2)),
                        filter_type='collar', id=int(collar)).filter_name)

            if productToken['promo_dict'] != '':
                promos_dict = productToken['promo_dict']

            try:
                if Products.objects.filter(scrapper_product_id=scrapper_product_id,
                                           user=productToken['user_no']).exists():
                    Products.objects.filter(scrapper_product_id=scrapper_product_id,
                                            user=productToken['user_no']).update(
                        scrapper_result_id=scrapper_result_id, scrapper_product_id=scrapper_product_id,
                        name=name, product_slug=product_slug, description=productToken['description'],
                        image=productToken['image'], all_images=productToken['images'],
                        petite_size=" | ".join(petite_sizes), regular_size=" | ".join(regular_sizes),
                        tall_size=" | ".join(tall_sizes), plus_size=" | ".join(plus_sizes),
                        short_size=" | ".join(short_sizes), long_size=" | ".join(long_sizes),
                        x_long_size=" | ".join(x_long_sizes),
                        color=color,
                        multicolor=productToken['multicolor'], display_color=productToken['display_color'],
                        material=" | ".join(materials), fit_type=" | ".join(fit_types),
                        characters=" | ".join(characters), closure=" | ".join(closures),
                        dress_length=" | ".join(dress_lengths), dress_style=" | ".join(dress_styles),
                        embellishment=" | ".join(embellishments), feature=" | ".join(features),
                        season=" | ".join(seasons), garment_care=" | ".join(garment_cares),
                        pattern=" | ".join(patterns), neckline=" | ".join(necklines), occasion=" | ".join(occasions),
                        sleeve_length=" | ".join(sleeve_lengths), sleeve_type=" | ".join(sleeve_types),
                        theme=" | ".join(themes), fastening_type=" | ".join(fastening_types),
                        cuff_style=" | ".join(cuff_styles), collar=" | ".join(collars), price=price,
                        price_highest=price_highest, sale_price=sale_price, sale_price_highest=sale_price_highest,
                        discount_percentage=discount_percentage, product_url=productToken['product_url'],
                        discount_percentage_highest=discount_percentage_highest, brand_id=brand_id, brand=brand,
                        brand_slug=brand_slug, store_name=store_name, store_logo=store_logo, store_url=store_url,
                        store_id=store_id, our_category_id=our_category_id, our_category_id_2=our_category_id_2,
                        our_category_name=our_category_name, our_category_name_2=our_category_name_2,
                        parent_category_id=parent_category_id, parent_category_name=parent_category_name,
                        parent_category_id_2=parent_category_id_2, parent_category_name_2=parent_category_name_2,
                        returns_accepted=productToken['returns_accepted'], user=productToken['user_no'],
                        benefits_charity=productToken['benefits_charity'],
                        climate_pledge_friendly=productToken['authenticity_guarantee'],
                        authenticity_guarantee=productToken['climate_pledge_friendly'],
                        promo_offer_type=" | ".join(promo_offer_types),
                        promo_offer_label=" | ".join(promo_offer_labels),
                        price_offer_type=" | ".join(price_offer_types),
                        price_offer_label=" | ".join(price_offer_labels),
                        shipping_offer_type=" | ".join(ship_offer_types),
                        shipping_offer_label=" | ".join(ship_offer_labels),
                        other_offer_type=" | ".join(other_offer_types),
                        other_offer_label=" | ".join(other_offer_labels),
                        promo_dict=promos_dict,
                        is_deleted=productToken['is_deleted'],
                        last_scrapper_update=datetime.datetime.now(), updated_at=datetime.datetime.now())
                else:
                    productSlugs = list(Products.objects.values_list('product_slug', flat=True))
                    existingProSlug = Enumerable(productSlugs).where(lambda x: x == product_slug).first_or_default()
                    if existingProSlug is not None:
                        newProduct = Products.objects.create(scrapper_result_id=scrapper_result_id,
                                                             scrapper_product_id=scrapper_product_id,
                                                             name=name, description=productToken['description'],
                                                             image=productToken['image'],
                                                             all_images=productToken['images'],
                                                             petite_size=" | ".join(petite_sizes),
                                                             regular_size=" | ".join(regular_sizes),
                                                             tall_size=" | ".join(tall_sizes),
                                                             plus_size=" | ".join(plus_sizes),
                                                             short_size=" | ".join(short_sizes),
                                                             long_size=" | ".join(long_sizes),
                                                             x_long_size=" | ".join(x_long_sizes),
                                                             multicolor=productToken['multicolor'], color=color,
                                                             display_color=productToken['display_color'],
                                                             material=" | ".join(materials),
                                                             fit_type=" | ".join(fit_types),
                                                             characters=" | ".join(characters),
                                                             closure=" | ".join(closures),
                                                             dress_length=" | ".join(dress_lengths),
                                                             dress_style=" | ".join(dress_styles),
                                                             embellishment=" | ".join(embellishments),
                                                             feature=" | ".join(features), season=" | ".join(seasons),
                                                             garment_care=" | ".join(garment_cares),
                                                             pattern=" | ".join(patterns),
                                                             neckline=" | ".join(necklines),
                                                             occasion=" | ".join(occasions),
                                                             sleeve_length=" | ".join(sleeve_lengths),
                                                             sleeve_type=" | ".join(sleeve_types),
                                                             theme=" | ".join(themes), brand=brand,
                                                             fastening_type=" | ".join(fastening_types),
                                                             cuff_style=" | ".join(cuff_styles),
                                                             collar=" | ".join(collars), sale_price=sale_price,
                                                             price_highest=price_highest, price=price,
                                                             sale_price_highest=sale_price_highest,
                                                             brand_slug=brand_slug, store_url=store_url,
                                                             product_url=productToken['product_url'], store_id=store_id,
                                                             discount_percentage=discount_percentage, brand_id=brand_id,
                                                             discount_percentage_highest=discount_percentage_highest,
                                                             store_name=store_name, store_logo=store_logo,
                                                             our_category_id=our_category_id,
                                                             our_category_id_2=our_category_id_2,
                                                             our_category_name=our_category_name,
                                                             our_category_name_2=our_category_name_2,
                                                             parent_category_id=parent_category_id,
                                                             parent_category_name=parent_category_name,
                                                             parent_category_id_2=parent_category_id_2,
                                                             parent_category_name_2=parent_category_name_2,
                                                             returns_accepted=productToken['returns_accepted'],
                                                             benefits_charity=productToken['benefits_charity'],
                                                             climate_pledge_friendly=productToken[
                                                                 'authenticity_guarantee'],
                                                             authenticity_guarantee=productToken[
                                                                 'climate_pledge_friendly'],
                                                             promo_offer_type=" | ".join(promo_offer_types),
                                                             promo_offer_label=" | ".join(promo_offer_labels),
                                                             price_offer_type=" | ".join(price_offer_types),
                                                             price_offer_label=" | ".join(price_offer_labels),
                                                             shipping_offer_type=" | ".join(ship_offer_types),
                                                             shipping_offer_label=" | ".join(ship_offer_labels),
                                                             other_offer_type=" | ".join(other_offer_types),
                                                             other_offer_label=" | ".join(other_offer_labels),
                                                             promo_dict=promos_dict,
                                                             is_deleted=productToken['is_deleted'],
                                                             user=productToken['user_no'],
                                                             last_scrapper_update=datetime.datetime.now())
                        product_slug = product_slug + "-" + str(newProduct.id)
                        Products.objects.filter(scrapper_result_id=scrapper_result_id,
                                                scrapper_product_id=scrapper_product_id).update(
                            product_slug=product_slug)
                    else:
                        Products(scrapper_result_id=scrapper_result_id, product_slug=product_slug, name=name,
                                 scrapper_product_id=scrapper_product_id, description=productToken['description'],
                                 all_images=productToken['images'], petite_size=" | ".join(petite_sizes),
                                 regular_size=" | ".join(regular_sizes),
                                 tall_size=" | ".join(tall_sizes), plus_size=" | ".join(plus_sizes),
                                 short_size=" | ".join(short_sizes), long_size=" | ".join(long_sizes),
                                 x_long_size=" | ".join(x_long_sizes),
                                 multicolor=productToken['multicolor'], color=color,
                                 display_color=productToken['display_color'],
                                 image=productToken['image'], material=" | ".join(materials),
                                 fit_type=" | ".join(fit_types), characters=" | ".join(characters),
                                 closure=" | ".join(closures), dress_length=" | ".join(dress_lengths),
                                 dress_style=" | ".join(dress_styles),
                                 embellishment=" | ".join(embellishments),
                                 feature=" | ".join(features), season=" | ".join(seasons),
                                 garment_care=" | ".join(garment_cares), pattern=" | ".join(patterns),
                                 neckline=" | ".join(necklines), occasion=" | ".join(occasions),
                                 sleeve_length=" | ".join(sleeve_lengths),
                                 sleeve_type=" | ".join(sleeve_types),
                                 theme=" | ".join(themes), fastening_type=" | ".join(fastening_types),
                                 cuff_style=" | ".join(cuff_styles), collar=" | ".join(collars),
                                 price_highest=price_highest, price=price, sale_price=sale_price,
                                 sale_price_highest=sale_price_highest, brand_slug=brand_slug,
                                 product_url=productToken['product_url'], store_id=store_id,
                                 discount_percentage=discount_percentage, brand_id=brand_id, brand=brand,
                                 discount_percentage_highest=discount_percentage_highest,
                                 store_name=store_name, store_logo=store_logo, store_url=store_url,
                                 our_category_id=our_category_id, our_category_id_2=our_category_id_2,
                                 our_category_name=our_category_name,
                                 our_category_name_2=our_category_name_2,
                                 parent_category_id=parent_category_id,
                                 parent_category_name=parent_category_name,
                                 parent_category_id_2=parent_category_id_2,
                                 parent_category_name_2=parent_category_name_2,
                                 returns_accepted=productToken['returns_accepted'],
                                 benefits_charity=productToken['benefits_charity'],
                                 climate_pledge_friendly=productToken['authenticity_guarantee'],
                                 authenticity_guarantee=productToken['climate_pledge_friendly'],
                                 promo_offer_type=" | ".join(promo_offer_types),
                                 promo_offer_label=" | ".join(promo_offer_labels),
                                 price_offer_type=" | ".join(price_offer_types),
                                 price_offer_label=" | ".join(price_offer_labels),
                                 shipping_offer_type=" | ".join(ship_offer_types),
                                 shipping_offer_label=" | ".join(ship_offer_labels),
                                 other_offer_type=" | ".join(other_offer_types),
                                 other_offer_label=" | ".join(other_offer_labels),
                                 promo_dict=promos_dict,
                                 is_deleted=productToken['is_deleted'], user=productToken['user_no'],
                                 last_scrapper_update=datetime.datetime.now()).save()

                proID = Products.objects.get(scrapper_product_id=scrapper_product_id, user=productToken['user_no'])
                if Product_Color_Sizes.objects.filter(product_id=proID).exists():
                    Product_Color_Sizes.objects.filter(product_id=proID).delete()

                for product_col_size in product_col_sizes:
                    Product_Color_Sizes(product_id=proID, color_map_id=product_col_size[1],
                                        color_name=product_col_size[2], color_price=product_col_size[3],
                                        size_map_id=product_col_size[4], size_type=product_col_size[5],
                                        price=product_col_size[6], sale_price=product_col_size[7]).save()

                for size_map in size_map_list:
                    if Size_Maps.objects.filter(our_size=size_map[0], size_type=size_map[2],
                                                size_name=size_map[3]).exists():
                        Size_Maps.objects.filter(our_size=size_map[0], size_type=size_map[2],
                                                 size_name=size_map[3]).update(our_size=size_map[0],
                                                                               our_size_slug=size_map[1],
                                                                               size_type=size_map[2],
                                                                               size_name=size_map[3],
                                                                               size_map_slug=size_map[4],
                                                                               updated_at=datetime.datetime.now())
                    else:
                        Size_Maps(our_size=size_map[0], our_size_slug=size_map[1], size_type=size_map[2],
                                  size_name=size_map[3], size_map_slug=size_map[4]).save()

                Price_Histories(product_id=proID, price=price, sale_price=sale_price).save()

                saved += 1
            except Exception as e:
                failed += 1
                ex = ShowException(e)
                context = {'Error': 'Error saving product data: ' + str(ex), 'return_data': []}
                return Response(context)
            continue
        except Exception as e:
            failed += 1
            ex = ShowException(e)
            context = {'Error': 'Error getting product data: ' + str(ex), 'return_data': []}
            return Response(context)

    context = {"flag": True, "total_saved": saved, "failed_to_save": failed}
    return Response(context)


def Slugify(text):
    text = unidecode.unidecode(text).lower()
    return re.sub(r'[\W_]+$', '', re.sub(r'[\W_]+', '-', text))


def ShowException(e):
    return traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)