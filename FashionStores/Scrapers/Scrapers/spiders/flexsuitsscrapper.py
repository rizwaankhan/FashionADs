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


class FlexSuitsScrapper(shopify):
    Spider_BaseClass.testingGender = 'Men'

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(FlexSuitsScrapper, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def GetProductUrls(self, homePageResponse):
        # ========== Category And Subcategory ==========#
        topCategoryNodes = homePageResponse.xpath(
            "//ul[@class='site-nav']/li[a[contains(span/text(),'New') or contains(span/text(),'suit') or contains(span/text(),'tuxedos') or contains(span/text(),'Shirts') or contains(span/text(),'Pants')]]")
        for topCategoryNode in topCategoryNodes:
            topCategoryTitle = topCategoryNode.xpath("./a/span/text()").get().strip()
            topCategorylink = topCategoryNode.xpath("./a/@href").get()
            if not topCategorylink.startswith(store_url):
                topCategorylink = store_url.rstrip('/') + topCategorylink
            categoryNodes = topCategoryNode.xpath(
                ".//*[a[contains(span/text(),'Suits') or contains(span/text(),'Tuxedo') or contains(span/text(),'Dress')]]")
            # /ul/li[a[contains(span/text(),'Tuxedo') or contains(span/text(),'Dress')]]/ul/li/a
            for categoryNode in categoryNodes:
                categoryTitle = categoryNode.xpath("./a/span/text()").get().strip()
                categorylink = categoryNode.xpath("./a/@href").get()
                if not categorylink.startswith(store_url):
                    categorylink = store_url.rstrip('/') + categorylink
                subCategoryNodes = categoryNode.xpath("./ul/li/a")
                if not subCategoryNodes:
                    category = topCategoryTitle + " " + categoryTitle
                    self.listing(categorylink, category)
                else:
                    for subCategoryNode in subCategoryNodes:
                        subCategoryTitle = subCategoryNode.xpath("./span/text()").get().strip()
                        subCategorylink = subCategoryNode.xpath("./@href").get()
                        if not subCategorylink.startswith(store_url):
                            subCategorylink = store_url.rstrip('/') + subCategorylink

                        # =================== BREADCRUM =================== #
                        category = topCategoryTitle + " " + categoryTitle + " " + subCategoryTitle
                        # ====================================== #
                        self.listing(subCategorylink, category)
        return Spider_BaseClass.AllProductUrls

    def listing(self, categorylink, category):
        CategoryLinkResponse = requests.get(categorylink)
        categoryPageResponse = HtmlResponse(url=categorylink, body=CategoryLinkResponse.text, encoding='utf-8')
        product_list = categoryPageResponse.xpath(
            "//a[contains(@class,'product-title')]/@href").extract()
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
                categoryPageResponse.xpath("///link[@rel='next']/@href").get()
            if not nextpageUrl.startswith(store_url):
                nextpageUrl = store_url.rstrip('/') + nextpageUrl
            self.listing(nextpageUrl, category)
        except:
            pass

    def IgnoreProduct(self, response):
        productAvailability = response.xpath("//link[@itemprop='availability']/@href").get().strip()
        if not 'InStock' in productAvailability:
            return True
        else:
            return False
