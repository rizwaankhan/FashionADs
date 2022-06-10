import ast
import csv
import os
import re
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FashionADs.settings")
django.setup()

from py_linq import Enumerable
from FashionStores.allfilters import *
from FashionStores.GetFilters import *
from FashionStores.models import *

requestHeader = {'Content-Type': 'application/json'}
domainAndUrl = 'https://django.adscombined.com/api/'  # local


# ================ GET AUTH TOKEN  =====================#
# def GetAuthorizationToken():
#     print('GETTING NEW AUTH TOKEN ....!')
#
#     loginUrl = domainAndUrl + 'login'
#     apiResponse = requests.post(url=loginUrl, data='{"email":"apiuser@gmail.com","password":"kasAU2ASLDa82"}',
#                                 headers=requestHeader, timeout=6000)
#     apiJson = json.loads(apiResponse.content)
#     authToken = 'Bearer ' + apiJson['token']
#     return authToken


def PostProducts():
    # Kamran = api_user_1,  Farhan = api_user_2, DellTesting = api_user_3
    # Use different user number

    userNo = 'api_user_2'
    if userNo == 'api_user_':
        raise NotImplementedError("User number cannot be null")

    totalValues = []
    stores = Store.objects.all()
    for store in stores:
        if store.Name != 'Adam Lippes':  # 24s Fivestory Fashion Nova Andy & Evan  Lord and Taylor
            continue
        resultId = ScrapResult.objects.filter(StoreId=store.Id).last()
        if resultId == '' or resultId is None:
            continue

        global offerTypesList
        offerTypesList, headerData, offerData = GettingData(store.Url)

        products = Product.objects.filter(StoreId=store.Id)
        proBrands = list(set(products.values_list('Brand')))
        if len(proBrands) == 1:
            storeNature = 'Brand'
        else:
            storeNature = 'Store'

        if not OurStore.objects.filter(StoreName=store.Name, Nature=storeNature).exists():
            addingStoreUrl = domainAndUrl + 'saveCsvStore'
            localStoreData = {"store_name": store.Name, "store_url": store.Url, "nature": storeNature, "promos": ""}
            PostToServer(addingStoreUrl, localStoreData)
            GetStoresDetail()

        if OurStore.objects.filter(StoreName=store.Name, Nature='Store').exists():
            ourStoreId = OurStore.objects.get(StoreName=store.Name, Nature='Store').StoreID
        else:
            ourStoreId = OurStore.objects.get(StoreName=store.Name, Nature='Brand').StoreID

        scrapResultId = ScrapResult.objects.filter(StoreId=store.Id).last().Id

        saveProUrl = domainAndUrl + 'save_products'

        for product in products:
            try:
                # if product.Url != 'https://adamlippes.com/products/sl-pleated-waist-dress-in-printed-voile':
                #     continue

                promoOfferList = []
                priceOfferList = []
                shipOfferList = []
                otherOfferList = []
                promoDict = {}
                if offerData:
                    promoOfferList = GetPromoOffer(product, promoDict)
                    priceOfferList = GetPriceOffer(headerData, offerData, promoDict)
                    shipOfferList = GetShippingOffer(headerData, offerData, product, promoDict)
                    otherOfferList = GetOtherOffer(headerData, offerData, product, promoDict)

                price = product.Price
                salePrice = product.SalePrice
                if salePrice == 0.0:
                    colSizePrice = price
                else:
                    colSizePrice = salePrice

                hasMultiColor = 0
                sizeDictList = []
                lockedColors = []
                colorDictList = []
                mappedSizes = []

                productSizes = ProductSize.objects.filter(ProductId=product.Id)
                colors = list(filter(None, productSizes.filter(Available=1).values_list('Color', flat=True).distinct()))
                if colors:
                    for color in colors:
                        if OurColor.objects.filter(ColorName=color).exists():
                            Sizes(productSizes, colSizePrice, [color, color], [colorDictList, sizeDictList],
                                  mappedSizes)
                        else:
                            multiColors = re.findall(r'[A-Z]\w+', color)
                            if len(multiColors) > 1:
                                hasMultiColor = 1
                                hasMatched = False
                                unMatchedClList = []
                                for multiColor in multiColors:
                                    if OurColor.objects.filter(ColorName=multiColor).exists():
                                        Sizes(productSizes, colSizePrice, [multiColor, color],
                                              [colorDictList, sizeDictList], mappedSizes)
                                        hasMatched = True
                                    else:
                                        unMatchedClList.append(multiColor)
                                if unMatchedClList and not hasMatched:
                                    unMatchedColor = " ".join(unMatchedClList)
                                    lockedColors.append(unMatchedColor)
                                    Sizes(productSizes, colSizePrice, [unMatchedColor, color],
                                          [colorDictList, sizeDictList], mappedSizes)
                            else:
                                lockedColors.append(color)
                                Sizes(productSizes, colSizePrice, [color, color], [colorDictList, sizeDictList],
                                      mappedSizes)
                else:
                    Sizes(productSizes, colSizePrice, ['Not Specified', ''], [colorDictList, sizeDictList],
                          mappedSizes)

                lockedSizes = Enumerable(sizeDictList).where(lambda x: x['our_size'] == '').select(
                    lambda y: y['size_name']).to_list()

                productFilterIDs = ProductFilterIDs.objects.filter(ProductUrl=product.Url).last()
                productFilters = ProductFilters.objects.filter(ProductUrl=product.Url).last()
                imgUrls = ast.literal_eval(product.ImageUrl)

                discountPerc = ''
                priceLowest = 0.0
                priceHighest = 0.0
                salePriceLowest = 0.0
                salePriceHighest = 0.0

                priceList = list(
                    filter(None, productSizes.filter(Available=1).values_list('Price', flat=True).distinct()))
                salePriceList = list(
                    filter(None, productSizes.filter(Available=1).values_list('SalePrice', flat=True).distinct()))

                if (priceList and salePriceList) and len(priceList) > 1:
                    price = 0.0
                    salePrice = 0.0

                    priceLowest = float(min(priceList))
                    priceHighest = float(max(priceList))
                    salePriceLowest = float(min(salePriceList))
                    salePriceHighest = float(max(salePriceList))

                    if salePriceLowest == 0.0:
                        salePriceLowest = salePriceHighest
                        salePriceHighest = priceHighest

                    if salePriceHighest != 0.0:
                        diffLowest = priceLowest - salePriceLowest
                        diffHighest = priceHighest - salePriceHighest
                        discountPerc = str(round(float(diffLowest / priceLowest * 100), 2)) + '-' + str(round(
                            float(diffHighest / priceHighest * 100), 2))
                else:
                    if salePrice != 0.0:
                        diff = price - salePrice
                        discountPerc = str(round(float(diff / price * 100), 2))

                try:
                    productData = {
                        "scrapper_result_id": scrapResultId,
                        "scrapper_product_id": product.Id,
                        "name": product.Name,
                        "description": product.Description,
                        "image": imgUrls[0],
                        "images": "|".join(imgUrls),
                        "price": price,
                        "sale_price": salePrice,
                        "price_lowest": priceLowest,
                        "sale_price_lowest": salePriceLowest,
                        "price_highest": priceHighest,
                        "sale_price_highest": salePriceHighest,
                        "discount_percentage": discountPerc,
                        "is_deleted": product.Deleted,
                        "multicolor": hasMultiColor,
                        "category_id": productFilterIDs.Category,
                        "store_id": ourStoreId,
                        "display_color": ",".join(colors),
                        "color_id": colorDictList,
                        "size": sizeDictList,
                        "promo_offer_type": promoOfferList,
                        "price_offer_type": priceOfferList,
                        "shipping_offer_type": shipOfferList,
                        "other_offer_type": otherOfferList,
                        "parent_category_id": productFilterIDs.ParentCategory,
                        "product_url": product.Url,
                        "material": productFilterIDs.Material.replace("None", ''),
                        "material_percentage": productFilterIDs.MaterialPercentage,
                        "fit_type": productFilterIDs.FitType.replace("None", ''),
                        "closures": productFilterIDs.Closure.replace("None", ''),
                        "cuff_styles": productFilterIDs.CuffStyle.replace("None", ''),
                        "fastening_type": productFilterIDs.FasteningType.replace("None", ''),
                        "collars": productFilterIDs.Collar.replace("None", ''),
                        "patterns": productFilterIDs.Pattern.replace("None", ''),
                        "seasons": productFilterIDs.Season.replace("None", ''),
                        "dress_lengths": productFilterIDs.DressLength.replace("None", ''),
                        "characters": productFilterIDs.Character.replace("None", ''),
                        "dress_styles": productFilterIDs.DressStyle.replace("None", ''),
                        "embellishments": productFilterIDs.Embellishment.replace("None", ''),
                        "features": productFilterIDs.Feature.replace("None", ''),
                        "garment_cares": productFilterIDs.GarmentCare.replace("None", ''),
                        "necklines": productFilterIDs.Neckline.replace("None", ''),
                        "occasions": productFilterIDs.Occasion.replace("None", ''),
                        "sleeve_lengths": productFilterIDs.SleeveLength.replace("None", ''),
                        "themes": productFilterIDs.Themes.replace("None", ''),
                        "sleeve_types": productFilterIDs.SleeveType.replace("None", ''),
                        "returns_accepted": 0,
                        "benefits_charity": 0,
                        "authenticity_guarantee": 0,
                        "climate_pledge_friendly": 0,
                        "brand": product.Brand,
                        "promo_dict": promoDict,
                        "user_no": userNo
                    }

                    lockedColor = " => ".join(lockedColors)
                    lockedSize = " => ".join(lockedSizes)
                    dressStyle = productFilters.DressStyle
                    occasion = productFilters.Occasion
                    material = productFilters.Material
                    materialPerc = productFilterIDs.MaterialPercentage
                    if dressStyle != 'Not Specified':
                        dressStyle = ''

                    if occasion != 'Not Specified':
                        occasion = ''

                    if re.search(r'\d+( |)%', material):
                        if len(list(set(materialPerc.split(',')))) == 1 and list(set(materialPerc.split(',')))[0] == 0:
                            materialPerc = ''
                        else:
                            materialPerc = sum(list(map(int, list(set(materialPerc.split(','))))))

                        if materialPerc == 100:
                            material = ''
                            materialPerc = ''
                        else:
                            materialData = []
                            for m in re.finditer(r'\d+( |)%(( |)\w+)|\w+( |)\d+( |)%', material, re.IGNORECASE):
                                materialData.append(m.group(0))

                            material = " => ".join(list(materialData))
                    else:
                        material = 'Not Specified'
                        materialPerc = 'Not Specified'

                    productId = Product.objects.filter(Url=product.Url, StoreId=store.Id, Name=product.Name)[0]
                    if LockedData.objects.filter(ProductUrl=product.Url).exists():
                        if (lockedColor and lockedSize and dressStyle and occasion and material and materialPerc) == '':
                            LockedData.objects.filter(ProductUrl=product.Url).delete()
                        else:
                            LockedData.objects.filter(ProductUrl=product.Url).update(ProductId=productId,
                                                                                     ScraperResultID=scrapResultId,
                                                                                     StoreName=store.Name,
                                                                                     ProductUrl=product.Url,
                                                                                     Color=lockedColor, Size=lockedSize,
                                                                                     DressStyle=dressStyle,
                                                                                     Occasion=occasion,
                                                                                     Material=material,
                                                                                     MaterialPercentage=materialPerc)
                    else:
                        if (lockedColor and lockedSize and dressStyle and occasion and material and materialPerc) == '':
                            pass
                        else:
                            LockedData(ProductId=productId, ScraperResultID=scrapResultId, StoreName=store.Name,
                                       ProductUrl=product.Url, Color=lockedColor, Size=lockedSize,
                                       DressStyle=dressStyle,
                                       Occasion=occasion, Material=material, MaterialPercentage=materialPerc).save()

                    totalValues.append(productData)
                except Exception as e:
                    print(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
                    continue
                if len(totalValues) >= 200:
                    PostToServer(saveProUrl, totalValues)
                    totalValues = []
            except Exception as e:
                print(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
                continue
        if len(totalValues) > 0:
            PostToServer(saveProUrl, totalValues)
            totalValues = []


def GettingData(storeUrl):
    csvPath = ''
    csvFile = ''
    try:
        csvPath = str((os.path.dirname(os.path.abspath(__file__)))).split('\FashionApp')[0]
        csvFile = open("FashionApp/Promotion.csv", "r")
    except:
        for root, dirs, files in os.walk(csvPath):
            for name in files:
                if name == "Promotion.csv":
                    csvFile = open(str(root) + "\\Promotion.csv", "r")

    csvreader = csv.reader(csvFile)
    headerData = next(csvreader)

    offerData = []
    for row in csvreader:
        if str(storeUrl).strip().rstrip('/') in row[headerData.index('Site Url')].strip().rstrip('/'):
            offerData = row
            break

    return OfferType, headerData, offerData


def GetID(offerFilter):
    return Enumerable(offerTypesList).where(lambda x: x[2] == offerFilter).select(
        lambda y: y[3]).first_or_default()


def GetPromoOffer(productObj, promoDict):
    proCategory = str(productObj.Category).lower()
    proSalePrice = float(productObj.SalePrice)

    promoOfferList = []
    if 'deal' in proCategory.lower():
        offerID = GetID('Deal')
        promoOfferList.append({"id": offerID, "offer_type_label": 'Deal'})
        promoDict["Deal"] = "Deal"
    else:
        promoDict["Deal"] = ""

    if 'new' in proCategory or 'new arrival' in proCategory:
        offerID = GetID('New Arrival')
        promoOfferList.append({"id": offerID, "offer_type_label": 'New Arrival'})
        promoDict["New Arrival"] = "New Arrival"
    else:
        promoDict["New Arrival"] = ""

    if 'sale' in proCategory.lower() or proSalePrice != 0.0:
        offerID = GetID('Sales')
        promoOfferList.append({"id": offerID, "offer_type_label": 'Sale'})
        promoDict["Sales"] = "Sale"
    else:
        promoDict["Sales"] = ""

    if 'clearance' in proCategory.lower():
        offerID = GetID('Clearance')
        promoOfferList.append({"id": offerID, "offer_type_label": 'Clearance'})
        promoDict["Clearance"] = "Clearance"
    else:
        promoDict["Clearance"] = ""

    if 'Week' in proCategory.lower() and 'ad' in proCategory.lower():
        offerID = GetID('Weekly Ad')
        promoOfferList.append({"id": offerID, "offer_type_label": 'Weekly Ad'})
        promoDict["Weekly Ad"] = "Weekly Ad"
    else:
        promoDict["Weekly Ad"] = ""

    if 'today' in proCategory.lower() and 'ad' in proCategory.lower():
        offerID = GetID('Today\'s Ad')
        promoOfferList.append({"id": offerID, "offer_type_label": 'Today\'s Ad'})
        promoDict["Today\'s Ad"] = "Today\'s Ad"
    else:
        promoDict["Today\'s Ad"] = ""

    return promoOfferList


def GetPriceOffer(headerData, offerData, promoDict):
    priceOfferList = []

    # Also based on product => to be verified
    priceMatch = str(offerData[headerData.index('Price match')]).title()
    if priceMatch != '' and priceMatch.lower() != 'no':
        offerID = GetID('Price Match')
        priceOfferList.append({"id": offerID, "offer_type_label": 'Price Matched'})
        promoDict["Price Match"] = "Yes"
    else:
        promoDict["Price Match"] = "No"

    # Also based on product => to be verified
    priceGuarantee = str(offerData[headerData.index('Price Gurantee')]).title()
    if priceGuarantee != '' and priceGuarantee.lower() != 'no':
        offerID = GetID('Price Guarantee')
        priceOfferList.append({"id": offerID, "offer_type_label": 'Price Guaranteed'})
        promoDict["Price Guarantee"] = "Yes"
    else:
        promoDict["Price Guarantee"] = "No"

    return priceOfferList


def GetShippingOffer(headerData, offerData, productObj, promoDict):
    shippingOfferList = []

    proCategory = str(productObj.Category).lower()
    proPrice = float(productObj.Price)
    proSalePrice = float(productObj.SalePrice)
    if proSalePrice != 0.0:
        proPrice = proSalePrice

    price = offerData[headerData.index('Price')]
    shipCost = offerData[headerData.index('Shipping Cost')]
    shipCode = offerData[headerData.index('Shipping Code')]
    shipType = offerData[headerData.index('Shipping Type')]
    if shipType == '':
        shipType = 'Standard'

    if price == '':
        if shipCost.lower() == 'free':
            shipping = 'Free ' + shipType + ' Shipping on All Order'
        else:
            shipping = '$' + shipCost + ' ' + shipType + ' Shipping'
    else:
        aboveRanges = []
        underRanges = []

        abovePrice = price.split('/')[0]
        underPrice = price.split('/')[1]

        if 'above' in abovePrice.lower() and 'under' in abovePrice.lower():
            for m in re.finditer(r'\d+(.?)\d+', abovePrice):
                aboveRanges.append(m.group(0))
            shipping = GetRangeShipping(proPrice, shipCost, aboveRanges, shipType, shipCode)
        elif 'above' in underPrice.lower() and 'under' in underPrice.lower():
            for m in re.finditer(r'\d+(.?)\d+', underPrice):
                underRanges.append(m.group(0))
            shipping = GetRangeShipping(proPrice, shipCost, underRanges, shipType, shipCode)
        else:
            abovePrice = re.search(r'\d+(.?)\d+', abovePrice).group(0)
            underPrice = re.search(r'\d+(.?)\d+', underPrice).group(0)
            shipping = GetShipping(proPrice, shipCost, abovePrice, underPrice, shipType, shipCode)

    offerID = GetID('Free Shipping')
    shippingOfferList.append({"id": offerID, "offer_type_label": shipping})
    promoDict["Free Shipping"] = shipping

    if shipCode != '':
        offerID = GetID('Shipping Code')
        shippingOfferList.append({"id": offerID, "offer_type_label": shipCode})
        promoDict["Shipping Code"] = shipCode
    else:
        promoDict["Shipping Code"] = ''

    returnLabel = ''
    returnOffer = offerData[headerData.index('Return')]
    if returnOffer != '' and returnOffer.lower() != 'no':
        for returnItem in list(returnOffer.split(',')):
            if '/' in returnItem:
                if 'except'.lower() in returnItem:
                    returnItem = returnItem.split('except')[0]

                if '$' in returnItem:
                    returnLabel = returnItem.split('/')[1].strip() + ' Charge within ' + returnItem.split('/')[
                        0].strip()
                elif 'free shipping' in shipping:
                    returnLabel = 'Free Return within ' + returnItem.split('/')[0].strip()
            else:
                if not ('sale' in returnItem.lower() or 'clearance' in returnItem.lower()) and (not (
                        'sale' in proCategory.lower() or 'clearance' in proCategory.lower()) or proSalePrice != 0.0):
                    returnLabel = 'Free Return within ' + returnItem.split('except')[0].strip()

        if returnLabel != '':
            offerID = GetID('Free Return')
            shippingOfferList.append({"id": offerID, "offer_type_label": returnLabel})
            promoDict["Free Return"] = returnLabel
        else:
            promoDict["Free Return"] = ''

    exchangeLabel = ''
    exchange = offerData[headerData.index('Exchange')]
    if exchange != '' and exchange.lower() != 'no':
        if 'yes' in exchange or 'free exchange' in exchange:
            exchangeLabel = 'Free Exchange'
        elif '/' in exchange:
            if '$' in exchange:
                exchangeLabel = exchange.split('/')[1].strip() + ' Charge'
            elif 'size' in exchange.lower():
                exchangeLabel = 'Only Exchanging Size'

            if 'days' in exchange.split('/')[0].strip():
                exchangeLabel = exchangeLabel + ' within ' + exchange.split('/')[0].strip()
        else:
            exchangeLabel = 'Free Exchange within ' + exchange.split('except')[0].strip()

        offerID = GetID('Free Exchange')
        shippingOfferList.append({"id": offerID, "offer_type_label": exchangeLabel})
        promoDict["Free Exchange"] = exchangeLabel
    else:
        promoDict["Free Exchange"] = ''

    deliveryTime = str(offerData[headerData.index('Delivery Time')]).title()
    if deliveryTime != '' and deliveryTime.lower() != 'no':
        offerID = GetID('Delivery Time')
        shippingOfferList.append({"id": offerID, "offer_type_label": deliveryTime})
        promoDict["Delivery Time"] = deliveryTime
    else:
        promoDict["Delivery Time"] = ''

    storePickUp = str(offerData[headerData.index('Store PickUp')]).title()
    if storePickUp != '' and storePickUp.lower() != 'no':
        offerID = GetID('Store Pickup')
        shippingOfferList.append({"id": offerID, "offer_type_label": 'Store PickUp'})
        promoDict["Store Pickup"] = 'Store PickUp'
    else:
        promoDict["Store Pickup"] = ''

    offerID = GetID('Shipping Type')
    shippingOfferList.append({"id": offerID, "offer_type_label": shipType})
    promoDict["Shipping Type"] = shipType

    return shippingOfferList


def GetOtherOffer(headerData, offerData, productObj, promoDict):
    otherOffersList = []

    # Also based on product => to be verified
    cashBack = str(offerData[headerData.index('CashBack')]).title()
    if cashBack != '' and cashBack.lower() != 'no':
        offerID = GetID('Cash Back')
        otherOffersList.append({"id": offerID, "offer_type_label": 'Cash Back'})
        promoDict["Cash Back"] = "Cash Back"
    else:
        promoDict["Cash Back"] = ''

    proCategory = str(productObj.Category).lower()
    proPrice = float(productObj.Price)
    proSalePrice = float(productObj.SalePrice)
    if proSalePrice != 0.0:
        proPrice = proSalePrice

    couponList = []
    couponCode = str(offerData[headerData.index('Coupon Code')]).title()
    if couponCode != '' and couponCode.lower() != 'no':
        for couponItem in list(couponCode.split(',')):
            if ('sale' in couponItem.lower() or 'clearance' in couponItem.lower()) and (
                    'sale' in proCategory.lower() or 'clearance' in proCategory.lower() or proSalePrice != 0.0):
                couponList.append(
                    'Get ' + couponItem.split('/')[0] + ' OFF Use Code: ' + couponItem.split('/')[1].split('(')[0])
            elif '$' in couponItem and proPrice >= float(
                    couponItem.split('/')[1].split('(')[1].split(')')[0].replace('$', '')):
                couponList.append(
                    'Get ' + couponItem.split('/')[0] + ' OFF Use Code: ' + couponItem.split('/')[1].split('(')[0])

    if couponList:
        coupons = 'PLUS => '.join(couponList)
        offerID = GetID('Coupon Codes')
        otherOffersList.append({"id": offerID, "offer_type_label": coupons})
        promoDict["Coupon Codes"] = coupons
    else:
        promoDict["Coupon Codes"] = ""

    # Based on CategoryPage or ProductPage tag, not only Category/Navigation
    if 'BOGO' in proCategory.capitalize():
        offerID = GetID('BOGO')
        otherOffersList.append({"id": offerID, "offer_type_label": 'BOGO'})
        promoDict["BOGO"] = 'BOGO'
    else:
        promoDict["BOGO"] = ""

    signUp = str(offerData[headerData.index('SignUp Reward')]).title()
    if signUp != '' and signUp.lower() != 'no':
        offerID = GetID('Signup Reward')
        otherOffersList.append({"id": offerID, "offer_type_label": signUp.title()})
        promoDict["Signup Reward"] = signUp.title()
    else:
        promoDict["Signup Reward"] = ""

    referral = str(offerData[headerData.index('Referral')]).title()
    if referral != '' and referral.lower() != 'no':
        offerID = GetID('Referral')
        otherOffersList.append({"id": offerID, "offer_type_label": referral.title()})
        promoDict["Referral"] = referral.title()
    else:
        promoDict["Referral"] = ""

    membership = str(offerData[headerData.index('MemberShip')]).title()
    if membership != '' and membership.lower() != 'no':
        offerID = GetID('Membership')
        membership = 'PLUS => '.join(list(membership.split(',')))
        otherOffersList.append({"id": offerID, "offer_type_label": membership.title()})
        promoDict["Membership"] = membership.title()
    else:
        promoDict["Membership"] = ""

    # Also based on product => to be verified
    appDownload = str(offerData[headerData.index('App Download')]).title()
    if appDownload != '' and appDownload.lower() != 'no':
        offerID = GetID('App Download')
        appDownload = 'PLUS => '.join(list(appDownload.split(',')))
        otherOffersList.append({"id": offerID, "offer_type_label": appDownload.title()})
        promoDict["App Download"] = appDownload.title()
    else:
        promoDict["App Download"] = ""

    youthDis = str(offerData[headerData.index('Youth Discount')]).title()
    if youthDis != '' and youthDis.lower() != 'no':
        offerID = GetID('Youth Discount')
        youthDis = 'PLUS => '.join(list(youthDis.split(',')))
        otherOffersList.append({"id": offerID, "offer_type_label": youthDis.title()})
        promoDict["Youth Discount"] = youthDis.title()
    else:
        promoDict["Youth Discount"] = ""

    studentDis = str(offerData[headerData.index('Student Discount')]).title()
    if studentDis != '' and studentDis.lower() != 'no':
        offerID = GetID('Student Discount')
        studentDis = 'PLUS => '.join(list(studentDis.split(',')))
        otherOffersList.append({"id": offerID, "offer_type_label": studentDis.title()})
        promoDict["Student Discount"] = studentDis.title()
    else:
        promoDict["Student Discount"] = ""

    militaryDis = str(offerData[headerData.index('Military Discount')]).title()
    if militaryDis != '' and militaryDis.lower() != 'no':
        offerID = GetID('Military Discount')
        militaryDis = 'PLUS => '.join(list(militaryDis.split(',')))
        otherOffersList.append({"id": offerID, "offer_type_label": militaryDis.title()})
        promoDict["Military Discount"] = militaryDis.title()
    else:
        promoDict["Military Discount"] = ""

    workerDis = str(offerData[headerData.index('Worker Discount')]).title()
    if workerDis != '' and workerDis.lower() != 'no':
        offerID = GetID('Worker Discount')
        workerDis = 'PLUS => '.join(list(workerDis.split(',')))
        otherOffersList.append({"id": offerID, "offer_type_label": workerDis.title()})
        promoDict["Worker Discount"] = workerDis.title()
    else:
        promoDict["Worker Discount"] = ""

    creditCardMember = str(offerData[headerData.index('Credit Card Member')]).title()
    if creditCardMember != '' and creditCardMember.lower() != 'no':
        offerID = GetID('Credit Card Member')
        creditCardMember = 'PLUS => '.join(list(creditCardMember.split(',')))
        otherOffersList.append({"id": offerID, "offer_type_label": creditCardMember.title()})
        promoDict["Credit Card Member"] = creditCardMember.title()
    else:
        promoDict["Credit Card Member"] = ""

    printableCoupon = str(offerData[headerData.index('Printable Coupon')]).title()
    if printableCoupon != '' and printableCoupon.lower() != 'no':
        offerID = GetID('Printable Coupon')
        otherOffersList.append({"id": offerID, "offer_type_label": 'Printable Coupon'})
        promoDict["Printable Coupon"] = 'Printable Coupon'
    else:
        promoDict["Printable Coupon"] = ""

    # Yet to handle gift card/voucher and gift product
    if 'gift' in proCategory.lower():
        if 'gift card' in productObj.Name.lower() or 'gift voucher' in productObj.Name.lower():
            offerID = GetID('Gift Cards')
            otherOffersList.append({"id": offerID, "offer_type_label": 'Gift Cards'})
            promoDict["Gift Cards"] = 'Gift Cards'
        else:
            promoDict["Gift Cards"] = ""

        if 'gift product' in productObj.Name.lower():
            offerID = GetID('Gift Products')
            otherOffersList.append({"id": offerID, "offer_type_label": 'Gift Products'})
            promoDict["Gift Products"] = 'Gift Products'
        else:
            promoDict["Gift Products"] = ""
    else:
        promoDict["Gift Cards"] = ""
        promoDict["Gift Products"] = ""
    return otherOffersList


def GetShipping(price, shipCost, abovePrice, underPrice, shipType, shipCode):
    if '/' in shipCost:
        aboveShipCost = shipCost.split('/')[0]
        if aboveShipCost.lower() == 'free' and float(price) >= float(abovePrice):
            if shipCode != '':
                shipping = 'Free ' + shipType + ' Shipping on Order $' + abovePrice + ' Use Code: ' + shipCode
            else:
                shipping = 'Free ' + shipType + ' Shipping on Order $' + abovePrice
        else:
            underShipCost = shipCost.split('/')[1]
            if underShipCost.lower() == 'free' and float(price) >= float(underPrice):
                if shipCode != '':
                    shipping = 'Free ' + shipType + ' Shipping on Order $' + underPrice + ' Use Code: ' + shipCode
                else:
                    shipping = 'Free ' + shipType + ' Shipping on Order $' + underPrice
            else:
                shipping = '$' + underShipCost + ' ' + shipType + ' Shipping'
    else:
        shipping = '$' + shipCost + ' ' + shipType + ' Shipping'

    return shipping.replace('-', ' to $')


def GetRangeShipping(price, shipCost, rangesPrice, shipType, shipCode):
    if '/' in shipCost:
        rangeShipCost = shipCost.split('/')[0]
        if rangeShipCost.lower() == 'free' and (
                float(rangesPrice[0]) <= float(price) <= float(rangesPrice[1])):
            if shipCode != '':
                return 'Free ' + shipType + ' Shipping on Order $' + rangesPrice[0] + ' - $' + rangesPrice[
                    1] + ' Use Code: ' + shipCode
            else:
                return 'Free ' + shipType + ' Shipping on Order $' + rangesPrice[0] + ' - $' + rangesPrice[1]
        else:
            underShipCost = shipCost.split('/')[1]
            if underShipCost.lower() == 'free' and (
                    float(rangesPrice[0]) <= float(price) <= float(rangesPrice[1])):
                if shipCode != '':
                    return 'Free ' + shipType + ' Shipping on Order $' + rangesPrice[0] + ' - $' + rangesPrice[
                        1] + ' Use Code: ' + shipCode
                else:
                    return 'Free ' + shipType + ' Shipping on Order $' + rangesPrice[0] + ' - $' + rangesPrice[1]
            else:
                return str('$' + underShipCost + ' ' + shipType + ' Shipping').replace('-', ' to $')
    else:
        return ('$' + shipCost + ' ' + shipType + ' Shipping').replace('-', ' to $')


def Sizes(productSizes, colSizePrice, colorList, colorSizeDictList, mappedColSizes):
    colSizeList = []
    if OurColor.objects.filter(ColorName__icontains=colorList[0]).exists():
        ourColorId = OurColor.objects.get(ColorName__icontains=colorList[0]).ColorID
    else:
        ourColorId = OurColor.objects.get(ColorName='Not Specified').ColorID

    fitTypes = list(
        productSizes.filter(Color__icontains=colorList[1]).values_list('FitType', flat=True).distinct())
    for fitType in fitTypes:
        sizes = list(
            productSizes.filter(Color__icontains=colorList[1], FitType=fitType, Available=1).values_list(
                'Size', 'MappedSize', 'Price', 'SalePrice'))
        if sizes:
            for size in sizes:
                existingColSize = Enumerable(mappedColSizes).where(
                    lambda x: x[0] == size[1] and x[1] == colorList[0]).first_or_default()
                if existingColSize:
                    continue

                priceList = list(
                    set(Enumerable(sizes).where(lambda x: x[1] == size[1]).select(lambda y: y[2]).to_list()))

                salePriceList = list(
                    set(Enumerable(sizes).where(lambda x: x[1] == size[1]).select(lambda y: y[3]).to_list()))

                if len(priceList) == 2:
                    price = str(priceList[0]) + '-' + str(priceList[1])
                else:
                    price = priceList[0]
                    if float(price) == 0.0:
                        price = colSizePrice

                if len(salePriceList) == 2:
                    salePrice = str(salePriceList[0]) + '-' + str(salePriceList[1])
                else:
                    salePrice = salePriceList[0]

                colSizeList.append({"our_size": size[1], "size_name": size[0], "size_type": fitType,
                                    "price": price, "sale_price": salePrice})
                mappedColSizes.append((size[1], colorList[0]))

                existingSize = Enumerable(colorSizeDictList[1]).where(
                    lambda x: x['our_size'] == size[1]).first_or_default()
                if not existingSize:
                    colorSizeDictList[1].append({"our_size": size[1], "size_name": size[0], "size_type": fitType})

    colorSizeDictList[0].append(
        {"id": ourColorId, "price": colSizePrice, "color_name": colorList[1],
         "sizes": colSizeList})


def PostToServer(reqUrl, reqJson):
    try:
        reqJson = json.dumps(reqJson)
        print(reqJson)
        saveData = requests.post(url=reqUrl, data=reqJson, headers=requestHeader, timeout=6000, verify=False)
        print(saveData.content)
    except Exception as e:
        print(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
        pass


# def RefreshCount():
#     try:
#         refreshUrl = domainAndUrl + 'refresh_counts'
#         refreshResp = requests.get(url=refreshUrl, headers=requestHeader, timeout=6000)
#         if not refreshResp and refreshResp.status_code != 200:
#             requestHeader['Authorization'] = GetAuthorizationToken()
#             refreshResp = requests.get(url=refreshUrl, headers=requestHeader, timeout=6000)
#
#         print(refreshResp.content)
#     except Exception as e:
#         print(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
#         pass
#     # time.sleep(5)


# ========================== END =======================#
if __name__ == '__main__':
    print('Getting Data....!')
    PostProducts()