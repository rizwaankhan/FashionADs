import os, sys, django
import re
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FashionADs.settings")
django.setup()

from ServerAPIs.models import *
from django.db.models import Q
from functools import reduce
from py_linq import Enumerable
import Levenshtein as lev


class ProductMatchingClass:
    def __init__(self):
        try:
            self.group_id = ProductMatched.objects.latest('Id').GroupId + 1
        except Exception as e:
            self.group_id = 1
        try:
            self.similar_group_id = ProductSimilarity.objects.latest('Id').GroupId + 1
        except Exception as e:
            self.similar_group_id = 1

    def FindMatching(self):
        allProducts = Products.objects.filter(is_deleted=0)
        for product in allProducts:
            print('ProductID: ', product.id)
            productSizes = Products.objects.get(id=product.id)
            priceList = list(
                filter(None, Product_Color_Sizes.objects.filter(product_id=productSizes).values_list('price',
                                                                                                     flat=True).distinct()))
            salePriceList = list(
                filter(None, Product_Color_Sizes.objects.filter(product_id=productSizes).values_list('sale_price',
                                                                                                     flat=True).distinct()))

            if len(priceList) > 1 and len(salePriceList) > 1:
                print('Size variation exists')
            else:
                colors = list(filter(None,
                                     Product_Color_Sizes.objects.filter(product_id=product.id).values_list('color_name',
                                                                                                           flat=True).distinct()))
                comparisonData = []
                if colors:
                    for color in colors:
                        if re.search(color, product.name):
                            nameWithColor = product.name
                        else:
                            nameWithColor = str(product.name + " - " + color).strip()
                        self.SearchProductInDB(product.id, nameWithColor, color, product.brand, product.store_id,
                                               'Comparison', 1)

                        self.SearchProductInDB(product.id, nameWithColor, color, product.brand, product.store_id,
                                               'Similarity', 1)

                if not comparisonData:
                    if colors:
                        onlyName = ''
                        for color in colors:
                            onlyName = str(product.name).replace(color, '').strip().rstrip('-')
                        comparisonData = self.SearchProductInDB(product.id, onlyName, '', product.brand,
                                                                product.store_id, 'Comparison', 0)
                        if not comparisonData:
                            self.SearchProductInDB(product.id, product.name, '', product.brand, product.store_id,
                                                   'Comparison', 0)
                        self.SearchProductInDB(product.id, onlyName, '', product.brand, product.store_id, 'Similarity',
                                               0)
                    else:
                        self.SearchProductInDB(product.id, product.name, '', product.brand, product.store_id,
                                               'Comparison', 0)

                        self.SearchProductInDB(product.id, product.name, '', product.brand, product.store_id,
                                               'Similarity', 0)

            self.group_id += 1
            self.similar_group_id += 1

    def SearchProductInDB(self, mainProductId, mainName, mainColor, mainBrand, storeId, searchType, colorMatched):
        if searchType == 'Comparison':
            groupId = self.group_id
            allProducts = Products.objects.filter(reduce(lambda x, y: x | y, [
                Q((~Q(store_id=storeId)), name__icontains=word, brand=mainBrand) for word in mainName.split(' ')]))

            for product in allProducts:
                colors = list(filter(None,
                                     Product_Color_Sizes.objects.filter(product_id=product.id).values_list('color_name',
                                                                                                           flat=True).distinct()))

                matchingName = ''
                matchingRatio = 0.0
                if colors and mainColor != '':
                    foundColor = Enumerable(colors).where(lambda x: x == mainColor).first_or_default()
                    if foundColor:
                        if re.search(foundColor, product.name):
                            matchingName = product.name
                        else:
                            matchingName = str(product.name + " - " + foundColor).strip()
                    else:
                        for color in colors:
                            if re.search(color, product.name):
                                matchingName = product.name
                            else:
                                matchingName = str(product.name + " - " + color).strip()
                            matchingRatio = self.ProductMatchingRatio(mainName, matchingName)
                            if matchingRatio > 0.85:
                                break
                else:
                    matchingName = product.name

                if matchingRatio == 0.0:
                    matchingRatio = self.ProductMatchingRatio(mainName, matchingName)

                if matchingRatio > 0.85:
                    filtersList = []
                    mainFilters = Products.objects.filter(id=mainProductId)[0]
                    filtersList = self.GetFilters(mainFilters, filtersList, mainProductId, groupId)

                    productFilters = Products.objects.filter(id=product.id)[0]
                    filtersList = self.GetFilters(productFilters, filtersList, product.id, groupId)

                    matchedFilter = self.MatchedFilters(filtersList[0], filtersList[1])
                    self.SavingComparisonData(matchedFilter, colorMatched)
            return []
        else:
            groupId = self.similar_group_id
            productObj = Products.objects.get(id=mainProductId)
            filterNames = (productObj.dress_length + " | " + productObj.dress_style).replace("Not Specified", "")

            allProducts = Products.objects.filter(reduce(lambda x, y: x | y,
                                                         [Q((~Q(id=mainProductId)), name__icontains=word) for word in
                                                          mainName.split(' ')]))
            allProducts = allProducts.filter(
                reduce(lambda x, y: x | y, [Q(dress_length__icontains=word) for word in filterNames.split(' | ')]))
            for product in allProducts:
                colors = list(filter(None,
                                     Product_Color_Sizes.objects.filter(product_id=product.id).values_list('color_name',
                                                                                                           flat=True).distinct()))
                if colors:
                    for color in colors:
                        onlyMainName = str(product.name).replace(color, '').strip().rstrip('-')
                        onlyName = str(mainName).replace(mainColor, '').strip().rstrip('-')
                        matchingRatio = self.ProductMatchingRatio(onlyMainName, onlyName)
                        if matchingRatio > 0.8:
                            filtersList = self.GetSimilarData(mainProductId, product.id, groupId)
                            self.SavingSimilarData(filtersList)
                else:
                    matchingRatio = self.ProductMatchingRatio(mainName, product.name)
                    if matchingRatio > 0.8:
                        filtersList = self.GetSimilarData(mainProductId, product.id, groupId)
                        self.SavingSimilarData(filtersList)

    def ProductMatchingRatio(self, nameForMatching, productName):
        productMatchingRatio = round(lev.ratio(nameForMatching.lower().strip(), productName.lower().strip()), 2)
        return productMatchingRatio

    def SavingComparisonData(self, matchedData, colorMatched):
        pro = matchedData[0]
        if colorMatched == 1 and ProductMatched.objects.filter(ProductId=Products.objects.filter(id=pro[0])[0],
                                                               ColorMatched=1, ParentProductId=pro[22]).exists():
            return
        elif colorMatched == 0 and ProductMatched.objects.filter(ProductId=Products.objects.filter(id=pro[0])[0],
                                                                 ColorMatched=0, ParentProductId=pro[22]).exists():
            return
        elif colorMatched == 0 and ProductMatched.objects.filter(ProductId=Products.objects.filter(id=pro[0])[0],
                                                                 ColorMatched=1, ParentProductId=pro[22]).exists():
            return
        elif colorMatched == 1 and ProductMatched.objects.filter(ProductId=Products.objects.filter(id=pro[0])[0],
                                                                 ColorMatched=0, ParentProductId=pro[22]).exists():
            groupData = ProductMatched.objects.filter(ProductId=Products.objects.filter(id=pro[0])[0], ColorMatched=0,
                                                      ParentProductId=pro[22])[0]
            ProductMatched.objects.filter(GroupId=groupData.GroupId).delete()

        ProductMatched(ProductId=Products.objects.filter(id=pro[0])[0], GroupId=pro[1], Character=pro[2],
                       Closure=pro[3], DressLength=pro[4], DressStyle=pro[5], Embellishment=pro[6], Feature=pro[7],
                       FitType=pro[8], GarmentCare=pro[9], Material=pro[10], Neckline=pro[11], Occasion=pro[12],
                       Pattern=pro[13], FasteningType=pro[14], CuffStyle=pro[15], Collar=pro[16], SleeveLength=pro[17],
                       SleeveType=pro[18], Themes=pro[19], Season=pro[20], ColorMatched=colorMatched,
                       ParentProductId=pro[22], MatchedPercentage=pro[21], DateCreated=datetime.now(),
                       DateUpdated=datetime.now()).save()

    def SavingSimilarData(self, similarData):
        pro = similarData[0]
        if ProductSimilarity.objects.filter(ProductId=Products.objects.filter(id=pro[0])[0],
                                            ParentProductId=pro[21]).exists():
            return

        ProductSimilarity(ProductId=Products.objects.filter(id=pro[0])[0], GroupId=pro[1], Character=pro[2],
                          Closure=pro[3], DressLength=pro[4], DressStyle=pro[5], Embellishment=pro[6],
                          Feature=pro[7], FitType=pro[8], GarmentCare=pro[9], Material=pro[10], Neckline=pro[11],
                          Occasion=pro[12], Pattern=pro[13], FasteningType=pro[14], CuffStyle=pro[15],
                          Collar=pro[16], SleeveLength=pro[17], SleeveType=pro[18], Themes=pro[19], Season=pro[20],
                          ParentProductId=pro[21], DateCreated=datetime.now(), DateUpdated=datetime.now()).save()

    def GetFilters(self, mainFilters, filtersList, productId, groupId):
        filter_Numbers = [productId, groupId]
        filter_Numbers.append('') if mainFilters.characters == 'Not Specified' else filter_Numbers.append(
            mainFilters.characters)
        filter_Numbers.append('') if mainFilters.closure == 'Not Specified' else filter_Numbers.append(
            mainFilters.closure)
        filter_Numbers.append('') if mainFilters.dress_length == 'Not Specified' else filter_Numbers.append(
            mainFilters.dress_length)
        filter_Numbers.append('') if mainFilters.dress_style == 'Not Specified' else filter_Numbers.append(
            mainFilters.dress_style)
        filter_Numbers.append('') if mainFilters.embellishment == 'Not Specified' else filter_Numbers.append(
            mainFilters.embellishment)
        filter_Numbers.append('') if mainFilters.feature == 'Not Specified' else filter_Numbers.append(
            mainFilters.feature)
        filter_Numbers.append('') if mainFilters.fit_type == 'Not Specified' else filter_Numbers.append(
            mainFilters.fit_type)
        filter_Numbers.append('') if mainFilters.garment_care == 'Not Specified' else filter_Numbers.append(
            mainFilters.garment_care)
        filter_Numbers.append('') if mainFilters.material == 'Not Specified' else filter_Numbers.append(
            mainFilters.material)
        filter_Numbers.append('') if mainFilters.neckline == 'Not Specified' else filter_Numbers.append(
            mainFilters.neckline)
        filter_Numbers.append('') if mainFilters.occasion == 'Not Specified' else filter_Numbers.append(
            mainFilters.occasion)
        filter_Numbers.append('') if mainFilters.pattern == 'Not Specified' else filter_Numbers.append(
            mainFilters.pattern)
        filter_Numbers.append('') if mainFilters.fastening_type == 'Not Specified' else filter_Numbers.append(
            mainFilters.fastening_type)
        filter_Numbers.append('') if mainFilters.cuff_style == 'Not Specified' else filter_Numbers.append(
            mainFilters.cuff_style)
        filter_Numbers.append('') if mainFilters.collar == 'Not Specified' else filter_Numbers.append(
            mainFilters.collar)
        filter_Numbers.append('') if mainFilters.sleeve_length == 'Not Specified' else filter_Numbers.append(
            mainFilters.sleeve_length)
        filter_Numbers.append('') if mainFilters.sleeve_type == 'Not Specified' else filter_Numbers.append(
            mainFilters.sleeve_type)
        filter_Numbers.append('') if mainFilters.theme == 'Not Specified' else filter_Numbers.append(mainFilters.theme)
        filter_Numbers.append('') if mainFilters.season == 'Not Specified' else filter_Numbers.append(
            mainFilters.season)

        filtersList.append(filter_Numbers)
        return filtersList

    def MatchedFilters(self, mainFilters, productFilters):
        indexCount = 0
        filterCount = 0
        matchedCount = 0
        updatedFilters = []
        updatedProdFilter = []

        for mainFilter in mainFilters:
            if indexCount == 0 or indexCount == 1:
                updatedProdFilter.append(productFilters[indexCount])
                indexCount += 1
                continue

            if mainFilter == '' or mainFilter == 'Not Specified':
                updatedProdFilter.append('')
            else:
                filterCount += 1
                mainList = list(str(mainFilter).split(' | '))
                productList = list(str(productFilters[indexCount]).split(' | '))
                interSectList = list(set(mainList).intersection(productList))
                if interSectList:
                    updatedProdFilter.append(",".join(interSectList))
                    matchedCount += 1
                else:
                    updatedProdFilter.append('')
            indexCount += 1

        updatedProdFilter.append(round(matchedCount / filterCount * 100, 2))
        updatedProdFilter.append(mainFilters[0])

        updatedFilters.append(updatedProdFilter)
        return updatedFilters

    def GetSimilarData(self, mainProductId, productId, groupId):
        filtersList = []
        filtersList = self.GetFilters(Products.objects.filter(id=productId)[0], filtersList, productId, groupId)
        filtersList[0].append(mainProductId)
        return filtersList


ProductMatchingClass().FindMatching()
