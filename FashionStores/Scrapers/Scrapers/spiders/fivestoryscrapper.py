import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DIR.parent.parent.parent.parent))
__package__ = DIR.name

import django

django.setup()
from Shopify import *
from scrapy import signals

store_url = sys.argv[4]


class FiveStoryScrapper(shopify):
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(FiveStoryScrapper, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def GetProductUrls(self, homePageResponse):
        # ========== Category And Subcategory ==========#
        topCategoryNodes = homePageResponse.xpath(
            "//ul[contains(@class,'site-nav')]/li/a[contains(text(),'Clothing') or contains(text(),'Sale') or contains(text(),'New')]")
        for topCategoryNode in topCategoryNodes:
            topCategoryTitle = topCategoryNode.xpath("./text()").get().strip()
            topCategorylink = topCategoryNode.xpath("./@href").get()
            if not topCategorylink.startswith(store_url):
                topCategorylink = store_url.rstrip('/') + topCategorylink
            topCategoryLinkResponse = requests.get(topCategorylink)
            topCategoryPageResponse = HtmlResponse(url=topCategorylink, body=topCategoryLinkResponse.text,
                                                   encoding='utf-8')
            categoryNodes = topCategoryPageResponse.xpath(
                "//div[contains(@class,'filter-group') and contains(h4/text(),'Type')]/div/ul/li/div/a[contains(text(),'Dress') or contains(text(),'Jumpsuits') or contains(text(),'Bodysuits') or contains(text(),'SET') or contains(text(),'SWIM')]")
            for categoryNode in categoryNodes:
                categoryTitle = categoryNode.xpath("./text()").get().strip()
                categorylink = categoryNode.xpath("./@href").get()
                if not categorylink.startswith(store_url):
                    categorylink = store_url.rstrip('/') + categorylink
                # =================== BREADCRUM ===================3
                category = 'Women' + " " + topCategoryTitle + " " + categoryTitle
                # ======================================#
                self.listing(categorylink, category)
        return Spider_BaseClass.AllProductUrls

    def listing(self, categorylink, category):
        CategoryLinkResponse = requests.get(categorylink)
        categoryPageResponse = HtmlResponse(url=categorylink, body=CategoryLinkResponse.text, encoding='utf-8')
        product_list = categoryPageResponse.xpath(
            "//div[@class='product-details__wrapper']/a/@href").extract()
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
            nextpageUrl = \
                categoryPageResponse.xpath("//link[@rel='next']/@href").extract()[0]
            if not nextpageUrl.startswith(store_url):
                nextpageUrl = store_url.rstrip('/') + nextpageUrl
            self.listing(nextpageUrl, category)
        except:
            pass

    def IgnoreProduct(self, response):
        if re.search('"availability":', response.text):
            productAvailability = response.text.split('"availability":')[1].split(',')[0].strip()
            if not 'InStock' in productAvailability:
                return True
            else:
                return False
