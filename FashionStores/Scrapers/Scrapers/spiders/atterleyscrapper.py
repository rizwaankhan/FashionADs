import json
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DIR.parent.parent.parent.parent))
__package__ = DIR.name

import django

django.setup()
from Shopify import *
from BaseClass import Spider_BaseClass
from scrapy import signals

store_url = sys.argv[4]


class AtterleyScrapper(Spider_BaseClass):
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(AtterleyScrapper, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def GetProductUrls(self, homePageResponse):
        # ========== Category And Subcategory ==========#
        topCategoryNodes = homePageResponse.xpath(
            "//nav[@class='desktop-navbar']/div/div[@class='desktop-navContent']/div[a[contains(text(),'Women')]]")
        for topCategoryNode in topCategoryNodes:
            topCategoryTitle = topCategoryNode.xpath("./a/text()").get().strip()
            topCategorylink = topCategoryNode.xpath("./a/@href").get()
            if not topCategorylink.startswith(store_url):
                topCategorylink = store_url.rstrip('/') + topCategorylink
            print("TOP CATEGORY  :", topCategoryTitle, "TOP CATEGORY LINK  :", topCategorylink)
            categoryNodes = topCategoryNode.xpath(
                "./div/div/div/div/ul/li[a[contains(text(),'Clothing')]]")
            for categoryNode in categoryNodes:
                categoryTitle = categoryNode.xpath("./a/text()").get().strip()
                categorylink = categoryNode.xpath("./a/@href").get()
                if not categorylink.startswith(store_url):
                    categorylink = store_url.rstrip('/') + categorylink
                print("CATEGORY  :", categoryTitle, "CATEGORY LINK  :", categorylink)
                subCategoryNodes = categoryNode.xpath(
                    "./div/div/div/div/div/ul/li/a[contains(text(),'Dresses') or contains(text(),'Jumpsuits') or contains(text(),'Nightwear')]")
                for subCategoryNode in subCategoryNodes:
                    subCategoryTitle = subCategoryNode.xpath("./text()").get().strip()
                    subCategorylink = subCategoryNode.xpath("./@href").get()
                    if not subCategorylink.startswith(store_url):
                        subCategorylink = store_url.rstrip('/') + subCategorylink
                    print("SUB CATEGORY  :", subCategoryTitle, "SUB CATEGORY LINK  :", subCategorylink)
                    if re.search('\?', subCategorylink):
                        subCategorylink = 'https' + subCategorylink.split('https' or 'http')[1].split('?')[0].strip()
                    category = topCategoryTitle + " " + categoryTitle + " " + subCategoryTitle
                    self.listing(subCategorylink, category)
        return Spider_BaseClass.AllProductUrls

    def listing(self, subCategorylink, category):
        subCategoryLinkResponse = requests.get(subCategorylink)
        subCategoryLinkResponse = HtmlResponse(url=subCategorylink, body=subCategoryLinkResponse.text,
                                               encoding='utf-8')
        product_list = subCategoryLinkResponse.xpath(
            "//div[contains(@class,'product-listing')]/div/div/a[contains(@class,'product-link')]/@href").extract()
        for productUrl in product_list:
            if not productUrl.startswith(store_url):
                productUrl = store_url.rstrip('/') + productUrl
                print('PRODUCT URL :', productUrl)
            Spider_BaseClass.AllProductUrls.append(productUrl)
            siteMapCategory = str(Spider_BaseClass.ProductUrlsAndCategory.get(productUrl)).replace('None', '')
            if siteMapCategory:
                Spider_BaseClass.ProductUrlsAndCategory[productUrl] = siteMapCategory + " " + category
            else:
                Spider_BaseClass.ProductUrlsAndCategory[productUrl] = category
        try:
            nextPageUrl = subCategoryLinkResponse.xpath("//div[contains(@class,'next')]/a/@href").extract()[0]
            if not nextPageUrl.startswith(store_url):
                nextPageUrl = store_url.rstrip('/') + nextPageUrl
                print("NEXT PAGE :", nextPageUrl)
            self.listing(nextPageUrl, category)
        except:
            pass

    def GetProducts(self, response):
        global productjson
        ignorProduct = self.IgnoreProduct(response)
        if ignorProduct == True:
            self.ProductIsOutofStock(GetterSetter.ProductUrl)
        else:
            responseJson = response.xpath("//script[@type='application/ld+json']/text()").get()
            productjson = json.loads(responseJson)
            self.GetProductInfo(response)

    def GetName(self, response):
        name = response.xpath("//div[@class='mb20 pName']/text()").get()
        return name

    def GetPrice(self, response):
        orignalPrice = response.xpath(
            "//div[@class='price serif']/div[@class='price-box']/p[@class='old-price']/span/text()").get()
        if orignalPrice != None:
            # return float(str(orignalPrice).replace('$', '').replace(',', ''))
            return float(str(orignalPrice).replace("Â£", '').replace("£", ''))
        else:
            orignalPrice = response.xpath(
                "//div[contains(@class,'product-detail-info')]/div/div[@class='price']/span/text()").get()
            # return float(str(orignalPrice).replace('$', '').replace(',', ''))
            return float(str(orignalPrice).replace("Â£", '').replace("£", ''))

    def GetSalePrice(self, response):
        salePrice = response.xpath(
            "//div[@class='price serif']/div[@class='price-box']/p[@class='special-price']/span/text()").get()
        if salePrice != None:
            return float(str(salePrice).replace("Â£", "").replace("£", ''))
        else:
            return 0

    def GetBrand(self, response):
        pass

    def GetImageUrl(self, response):
        imageUrls = []
        if re.search('productGallery:', response.text):
            imageList = response.text.split('productGallery:')[1].split('},attribute')[0]
            jtxt = re.sub(r'\b([a-zA-Z]+):("[^"]+"[,\n}])', r'"\1":\2', imageList).replace(',video:null',
                                                                                           ',"video":null')
            imageJson = json.loads(jtxt)
            for image in imageJson:
                imageurl = image['src']
                imageUrls.append(imageurl)
        print(imageUrls)
        return imageUrls

    def GetDescription(self, response):
        return response.xpath("//div[@id='proDesc']/p/text()").get()

    def GetSizes(self, response):
        productSizes = []
        sku = productjson['sku']
        colorName = self.GetSelectedColor(response)
        sizeOptions = response.xpath("//input[@data-attribute='size' or @data-attribute='Size']/@value").extract()
        for size in sizeOptions:
            prodId = sku + '_' + size

            for sizeValue in productjson['offers']:
                if sizeValue['sku'] == prodId:
                    if 'InStock' in sizeValue['availability']:
                        available = True
                        sizelist = str(colorName), str(size), available, 0.0, 0.0
                        productSizes.append(sizelist)
        return productSizes

    def GetCategory(self, response):
        filterList = []
        if GetterSetter.ProductUrl in Spider_BaseClass.ProductUrlsAndCategory:
            categories = Spider_BaseClass.ProductUrlsAndCategory[GetterSetter.ProductUrl]
            for category in str(categories).split('$'):
                filterList.append(category)
        filters = '$'.join(map(str, filterList))
        return filters

        # for filter in shopify.ProductJson['tags']:
        #     filterList.append(filter)
        # filters = '$'.join(map(str, filterList))
        # return filters
