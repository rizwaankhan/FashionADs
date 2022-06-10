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


class SoleilBlueScrapper(shopify):
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SoleilBlueScrapper, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def GetProductUrls(self, homePageResponse):
        # ========== Category And Subcategory ==========#
        topCategoryNodes = homePageResponse.xpath(
            "//ul[contains(@class,'mainMenu')]/li[a[contains(text(),'New Arrivals') or contains(text(),'Clothing ') or contains(text(),'Swim ')]]")
        for topCategoryNode in topCategoryNodes:
            topCategoryTitle = topCategoryNode.xpath("./a/text()").get().strip()
            topCategorylink = topCategoryNode.xpath("./a/@href").get()
            if not topCategorylink.startswith(store_url):
                topCategorylink = store_url.rstrip('/') + topCategorylink
            categoryNodes = topCategoryNode.xpath(
                "./ul/li/a[contains(text(),'Dresses') or contains(text(),'Cover ups') or contains(text(),'One pieces')]")
            if categoryNodes:
                for categoryNode in categoryNodes:
                    categoryTitle = categoryNode.xpath("./text()").get().strip()
                    categorylink = categoryNode.xpath("./@href").get()
                    if not categorylink.startswith(store_url):
                        categorylink = store_url.rstrip('/') + categorylink
                    category = 'Women ' + topCategoryTitle + " " + categoryTitle
                    self.listing(categorylink, category)
            else:
                category = 'Women ' + topCategoryTitle
                self.listing(topCategorylink, category)
        return Spider_BaseClass.AllProductUrls

    def listing(self, categorylink, category):
        categoryLinkResponse = requests.get(categorylink)
        categoryLinkResponse = HtmlResponse(url=categorylink, body=categoryLinkResponse.text, encoding='utf-8')

        product_list = categoryLinkResponse.xpath("//div[contains(@class,'thumbnail__caption')]/a/@href").extract()
        for productUrl in product_list:
            if not productUrl.startswith(store_url):
                productUrl = store_url.rstrip('/') + productUrl
            productUrl = self.GetCanonicalUrl(productUrl)
            Spider_BaseClass.AllProductUrls.append(productUrl)
            siteMapCategory = str(Spider_BaseClass.ProductUrlsAndCategory.get(productUrl)).replace('None', '')
            if siteMapCategory:
                Spider_BaseClass.ProductUrlsAndCategory[productUrl] = siteMapCategory + " " + category
            else:
                Spider_BaseClass.ProductUrlsAndCategory[productUrl] = category
        try:
            nextPageUrl = categoryLinkResponse.xpath("//link[@rel='next']/@href").extract()[0]
            if not nextPageUrl.startswith(store_url):
                nextPageUrl = store_url.rstrip('/') + nextPageUrl
            self.listing(nextPageUrl, category)
        except:
            pass

    def GetProducts(self, response):
        ignorProduct = self.IgnoreProduct(response)
        if ignorProduct == True:
            self.ProductIsOutofStock(GetterSetter.ProductUrl)
        shopify.productJson = json.loads(self.SetProductJson(response))
        categoryAndName = shopify.GetCategory(self, response) + " " + self.GetName(response)
        if (re.search(r'\b' + 'New Arrivals' + r'\b', categoryAndName, re.IGNORECASE)) and not \
                re.search(r'\b((shirt(dress?)|jump(suit?)|dress|romepr|set|gown|suit|caftan)(s|es)?)\b',
                          categoryAndName,
                          re.IGNORECASE):
            print('Skipping Non Dress Product')
            self.ProductIsOutofStock(GetterSetter.ProductUrl)
        else:
            self.GetProductInfo(response)

    def GetName(self, response):
        color = self.GetSelectedColor(response)
        name = shopify.GetName(self, response)
        if not color == '' and not re.search(color, name):
            name = name + '-' + color
        return name

    def GetSelectedColor(self, response):
        try:
            return response.xpath(
                "//div[@class='swatch clearfix'][div[@class='option_title' and contains(text(),'Color')]]/div/div/text()").get().strip()
        except:
            return ''

    def IgnoreProduct(self, response):
        if re.search('"availability":', response.text):
            productAvailability = response.text.split('"availability":')[1].split(',')[0].strip()
            if not 'InStock' in productAvailability:
                return True
            else:
                return False

    def GetDescription(self, response):
        baseDesc = shopify.GetDescription(self, response)
        description = response.xpath(
            "//div[@id='product-here']//div[contains(@class,'details-body')]/ul[contains(@class,'product-details-ul') or contains(@class,'product-fabrication-ul')]/li/text()").extract()
        description = ' '.join(map(str, description))
        return baseDesc + description
