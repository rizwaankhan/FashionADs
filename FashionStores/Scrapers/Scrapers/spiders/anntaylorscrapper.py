import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DIR.parent.parent.parent.parent))
__package__ = DIR.name

import django

django.setup()
from BaseClass import *
from scrapy import signals

store_url = sys.argv[4]


class AnntaylorScrapper(Spider_BaseClass):
    Spider_BaseClass.cookiesDict = {"_IntlCtr": "US", "_IntlCur": "USD"}

    # Spider_BaseClass.cookiesDict = {
    #     'Cookie': 's_ppvl=Homepage%2C15%2C15%2C145%2C1366%2C145%2C1366%2C768%2C1%2CP; s_ppv=Homepage%2C47%2C15%2C445%2C1366%2C342%2C1366%2C768%2C1%2CP; RT="z=1&dm=anntaylor.com&si=0063714e-b363-415b-b5d3-c0e5ef1b9288&ss=l0i34r06&sl=3&tt=7i4&obo=1&rl=1&nu=1nvnfdp1&cl=3t6n&ld=3tpo&r=3733s14a&ul=3tpq"; dtSa=false%7CC%7C14%7CUPDATE%20COUNTRY%7Cj1.10.1%7C1646741275429%7C341220276_458%7Chttps%3A%2F%2Fwww.anntaylor.com%2F%7C%7C%7C%7C; JSESSIONID=zXdpbLzvrFeZndy9cJgtr8X777HqtOY3od_7X-oGlo3S2Wlef1WC!-762725635; throttle=iad; orderId=112438830689; orderDetails=; _IntlCtr=US; _IntlCur=USD; b1pi=!tSUMVcoFjf0BfmN2UMO5J3ZIiaaKZjgmJWhbyIsaiIO66Slf5ujv8hX3J72E88EXHLqxe4LQ0YMHPIs=; AKA_FEO=FALSE; AKA_A2=A; _abck=0A2216EB00F41635F439509CE8D120A0~0~YAAQmUgRYGuUIWl/AQAA58tsaQemj2Y64fV4ywcZrsRDIDHVFJWYRAAaRMX52xoC3XTO8E9/RybjXjmmcRYJ1oDqa+00/bBes/y2v8hNE/PM35M0R3byzSERN3IE7pldBxOak7/t3PtfjxwoEMuokVrDD2m+IAfCGdtpbyvZMQN2JjDF6zttqVEQZmgBa+E8TKf535hrZcfe7NOId54YJuCvrs0XZSRIRsEfpux239aI72tCQqEF5rgd+u9HIwiSBCv2b7LRtyDsE1bo3YMkXnR0p43w2q9QwucL2waNwm0BNJ7W1S8z0piCEuZ8AKU5D2C9YHK2NwhrRYsRAkMHDxsZou/FVDrsJKLRtfCp8RCU0kukeupqX8K/321ibAEBBNexiqAGSQnKhfDgX+H2pdy3TdjBAzEmo0PGlA==~-1~||-1||~-1; ak_bmsc=0A19C844F68D5BA8D2740A7FD52D78EA~000000000000000000000000000000~YAAQmUgRYFKUIWl/AQAAbL5saQ+fSQ52D67Igj3zL0QSMxZYu0dVEgKQgphxaI6jK0xIMBcO76GSJgW2lmX5bE/BznYaEZtlEv+HlQJd1pL+Ka6jOhi5mRIxou5iXFnN8m8FCaunw+TwRxFb1o+VkJ/GlEOfn3aXEwUD8+qV0BYf/fkCvx8Dq1vie3Z9eac5TwlJ5orlMl4iZljnMEppjaRV/ei3IMUT3N8ihwsRVeDiSPo3DetGtZQEtjiPoqAP8GA1CDa369DHGeTSUH2oLiTAP3C/anEtA2QO1juuFG4jCPBYFs1672CSVOePfQsGYyUG2WC5mPOyywkzI4tgMx8jEWv0ub48ZNz/m83HVxtoVrJ0Hg1Od3u8ntYzEQzvTMLqwr+nGQlifuk=; bm_sz=56FC43FCDC7214F5A651649325BB092D~YAAQmUgRYFOUIWl/AQAAbL5saQ8fsmcjVTqVU82+JiqlzKDWWyvvlTMzvncYeMxDa8AASVpMaz2yl/jVRV+rOWTKC1sDn8jvaVt3AwvEkGYkI4lbMw0Pgp9bvtFblvEcFnt2ZIYtlQVzRAiW7d6WyuxewAkDjtDN7/vrHJl0+XAiiwYZI6Tqa/L8ms34+l5K0ueRNjICXfXhB91ZK8bqmoTojDHPStgaMnSQKPlskmAG5xeqxfdTWKA7oAlh+DOSpHIrnrd1Xyw17PZ9i97V04bwbUcbAy+oDkRyt5kkhDbUPg+N5q4=~3749700~3356724; __rpckx=0!eyJ0NyI6eyIxIjoxNjQ2NzQxMjE3NjQ4fSwidDd2Ijp7IjEiOjE2NDY3NDEyMTc2NDh9LCJpdGltZSI6IjIwMjIwMzA4LjEyMDYiLCJlYyI6M30~; __rpck=0!PTAhZXlKME55STZlMzBzSW5RM2RpSTZlMzBzSW1sMGFXMWxJam9pTWpBeU1qQXpNRGd1TVRJd05TSXNJbVZqSWpveUxDSjBPQ0k2ZXlJMklqb3hOalEyTnpReE1qQTVPRFl4Zlgwfg~~; bm_sv=6037FF75508C0ED250ECE6CDCD56D556~8/r6Vm3o591i1Fqn+Z3eMdKah1Wqdi0XeYKMNCm6gKDPTqMEigpP9ZlolwdbwyoeG9yHcMP3C9D3NqmvCV9lbuHSSjxh7DQOzKKXHOB5U0NBskGJGgAJImJ88nwcq1CrRxMK+hkfmtFKN3ECJc6XbLuQnExYw/I2t/x9jBIDCgc=; AMCV_B6761CFE533096CB0A490D45%40AdobeOrg=-2121179033%7CMCIDTS%7C19060%7CMCMID%7C41158728249918599560841976373814660949%7CMCAAMLH-1647346011%7C3%7CMCAAMB-1647346011%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1646748413s%7CNONE%7CMCSYNCSOP%7C411-19067%7CMCAID%7CNONE%7CvVersion%7C5.3.0; at_check=true; mbox=session#29987c3ff9974bb198228ee7410d8737#1646743075|PC#29987c3ff9974bb198228ee7410d8737.38_0#1709986014; at_wlcme=1; AMCVS_B6761CFE533096CB0A490D45%40AdobeOrg=1; s_ecid=MCMID%7C41158728249918599560841976373814660949; isRetina=false; isCardProgramMember=false; isLoyaltyEnrolled=false; accountCreated=; _cs_mk_aa=0.06470041496527479_1646741214666; s_nr30=1646741276128-New; gpv_p5=Homepage; s_dl=1; gpv_pn=Homepage; s_cc=true; __rutmb=166591726; __rutma=166591726-ud-gm-4j-1p-ktquq92g7ijlh2kz5avz-1646741217648.1646741217648.1646741217648.1.1.1; __ruid=166591726-ud-gm-4j-1p-ktquq92g7ijlh2kz5avz-1646741217648; __rcmp=0!bj1fZ2MsZj1nYyxzPTEsYz0xNDMwLHRyPTEwMCxybj0zNTAsdHM9MjAyMjAzMDguMTIwNixkPXBjO249c2IxLGY9c2Iscz0xLGM9MTAwMyx0PTIwMTYwODE2LjAwMDk7bj1ydyxmPXJ3LHM9MSxjPTEwMDAsdD0yMDE2MDgxNi4wMDA3; s_ppn=Homepage; dtCookie=v_4_srv_1_sn_BO5J02RREIQJMISERA7BJ42GSERI1QV3_app-3Ac1332b7b26e61ef2_0_ol_0_perc_100000_mul_1; rxVisitor=16467412202875PAC8ID5NS06SVEEJGC1FL8TL3R77GSR; dtPC=1$341220276_458h14vASMPWOEPHCCEDCOEHVPLGPFWOUUFOPJC-0e0; rxvt=1646743075446|1646741220289; dtLatC=17; _scid=a4ef0d9f-f68f-4f26-bf31-279632c82241; _cs_c=0; _cs_cvars=%7B%221%22%3A%5B%22Page%20Name%22%2C%22Homepage%22%5D%2C%222%22%3A%5B%22Page%20Type%22%2C%22Homepage%22%5D%2C%2211%22%3A%5B%22Cart%20Items%20Count%22%2C%220%22%5D%2C%2212%22%3A%5B%22Login%20Status%22%2C%22Anonymous%22%5D%7D; _cs_id=8798a233-3da4-a4a0-930d-ed8ecfa6f22f.1646741220.1.1646741220.1646741220.1.1680905220729; _cs_s=1.0.0.1646743020730; _uetsid=428500609ed811ecb2064feb432a0415; _uetvid=4284e5509ed811ec9dc78f75e50544d7; stc115491=tsa:1646741220855.467087202.946784.9907666054023095.79:20220308123700|env:1%7C20220408120700%7C20220308123700%7C1%7C1050439:20230308120700|uid:1646741220855.1100090537.158535.115491.1723730424.:20230308120700|srchist:1050439%3A1%3A20220408120700:20230308120700; _mibhv=anon-1646741220865-5142097693_7208; _gcl_au=1.1.1837799037.1646741221; mp_ann_taylor_mixpanel=%7B%22distinct_id%22%3A%20%2217f696cee7f2e1-0acd3ea0f9a62b8-4c3e227d-100200-17f696cee803b5%22%2C%22bc_persist_updated%22%3A%201646741220994%7D; _ga=GA1.2.1251671566.1646741222; _gid=GA1.2.2146911027.1646741222; _gat=1; mdLogger=false; kampyle_userid=2f1b-51d8-afc0-41f9-38a4-e0cc-403c-42d2; kampyleUserSession=1646741222742; kampyleSessionPageCounter=1; kampyleUserSessionsCount=1; bc_invalidateUrlCache_targeting=1646741222923; cd_user_id=17f696cf9f759e-09bcf80272cb0c-4c3e227d-100200-17f696cf9f8595; bluecoreNV=true; _pin_unauth=dWlkPU5UbGxPVEkyT0RFdE9EVTFNeTAwWkRoakxUZzVabVV0WWpjM09UVTROV1UyTkdNeg; _clck=u067ts|1|ezl|0; _sctr=1|1646679600000; _fbp=fb.1.1646741226376.782791097; _clsk=vcxn9l|1646741226570|1|1|f.clarity.ms/collect; xyz_cr_100329_et_114==&cr=100329&wegc=&et=114&ap=; cto_bundle=qzlHr19MTWE3WmF4YVVhSG5aQUROcUlvN2lmMCUyQmhNMnFPODFlc3J3aExsSEZPSTRvREFDbXBtSnFaMzVMUCUyQjh3dTBDR1lQWURkTlJPNXhtRURHVzNxN0FDNTZ5blMyNSUyRmd3RUslMkZuVlpQY0pKbGY3TG1wZmdOUmx3QVl4WmF3d0slMkZFczJRakFWOFBUUHlUZnFZaDhzYnNvaXJnJTNEJTNE; s_sq=%5B%5BB%5D%5D'}

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(AnntaylorScrapper, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def GetProductUrls(self, homePageResponse):
        # ========== Category And Subcategory ==========#
        topCategoryNodes = homePageResponse.xpath(
            "//nav/div/div[contains(@class,'sub-nav-wrapper')][a[contains(strong/text(),'Clothing')  or contains(strong/text(),'Petites') or contains(strong/text(),'Sale')]]")
        for topCategoryNode in topCategoryNodes:
            topCategoryTitle = topCategoryNode.xpath("./a/strong/text()").get().strip()
            topCategorylink = topCategoryNode.xpath("./a/@href").get().strip()
            if not topCategorylink.startswith(store_url):
                topCategorylink = store_url.rstrip('/') + topCategorylink
            topCategoryLinkResponse = requests.get(topCategorylink)
            topCategoryLinkResponse = HtmlResponse(url=topCategorylink, body=topCategoryLinkResponse.text,
                                                   encoding='utf-8')
            categoryNodes = topCategoryLinkResponse.xpath(
                "//div[@data-component='LeftNavigation']/a[contains(text(),'Clothing') or contains(text(),'Sale') or contains(text(),'Petites')]")
            for categoryNode in categoryNodes:
                categoryTitle = categoryNode.xpath("./text()").get().strip()
                if categoryNode.xpath(
                        "./following-sibling::nav/a[contains(text(),'Dress') or contains(text(),'Sleep')]"):
                    subCategoryNodes = categoryNode.xpath(
                        "./following-sibling::nav/a[contains(text(),'Dress') or contains(text(),'Sleep')]")
                    for subCategoryNode in subCategoryNodes:
                        subCategoryTitle = subCategoryNode.xpath("./text()").get().strip()
                        subCategorylink = subCategoryNode.xpath("./@href").get().strip()
                        if not subCategorylink.startswith(store_url):
                            subCategorylink = store_url.rstrip('/') + subCategorylink
                        category = "Women " + topCategoryTitle + " " + categoryTitle + " " + subCategoryTitle
                        print("Bread crum : ", category)
                        self.listing(subCategorylink, category)
                if categoryNode.xpath(
                        "./following-sibling::nav/div/a[contains(text(),'Dress') or contains(text(),'Suits')]/following-sibling::nav/a[contains(text(),'Dress')]"):
                    subCategoryNodes = categoryNode.xpath(
                        "./following-sibling::nav/div/a[contains(text(),'Dress') or contains(text(),'Suits')]/following-sibling::nav/a[contains(text(),'Dress')]")
                    for subCategoryNode in subCategoryNodes:
                        subCategoryTitle = subCategoryNode.xpath("./text()").get().strip()
                        subCategorylink = subCategoryNode.xpath("./@href").get().strip()
                        if not subCategorylink.startswith(store_url):
                            subCategorylink = store_url.rstrip('/') + subCategorylink
                        category = "Women " + topCategoryTitle + " " + categoryTitle + " " + subCategoryTitle
                        print("Bread crum : ", category)
                        self.listing(subCategorylink, category)
        return Spider_BaseClass.AllProductUrls

    def listing(self, categorylink, category):
        categoryLinkResponse = requests.get(categorylink)
        categoryLinkResponse = HtmlResponse(url=categorylink, body=categoryLinkResponse.text, encoding='utf-8')
        product_list = categoryLinkResponse.xpath(
            "//ul/li/div[@class='product-wrap']/div/a/@href").extract()
        for productUrl in product_list:
            if 'dress' in productUrl:
                print(productUrl)
                if not productUrl.startswith(store_url):
                    productUrl = store_url.rstrip('/') + productUrl
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
        global productjson
        ignorProduct = self.IgnoreProduct(response)
        if ignorProduct == True:
            self.ProductIsOutofStock(GetterSetter.ProductUrl)
        else:
            global productjson
            productjson = HtmlResponse(url='None', body=response.text, encoding='utf-8')
            productjson = json.loads(productjson.text.split('var productIndex = ')[1].split(' var ')[0])
            productjson = productjson['products'][0]
            self.GetProductInfo(response)

    def GetName(self, response):
        name = productjson['displayName']
        return name

    def GetPrice(self, response):
        orignalPrice = productjson['listPrice']
        if orignalPrice != None:
            return float(str(orignalPrice).replace('$', '').replace(',', ''))
        else:
            return 0

    def GetSalePrice(self, response):
        salePrice = productjson.get('salePrice')
        if salePrice != None:
            return float(str(salePrice).replace("$", "").replace(',', ''))
        else:
            return 0

    def GetBrand(self, response):
        return 'Anna Taylor'

    def GetImageUrl(self, response):
        imageUrls = []
        try:
            images = productjson['initialReduxState']['product']['asset_files']
            for image in images:
                imageUrls.append(image['s3_url'])
            return imageUrls
        except:
            images = response.xpath(
                "//div[contains(@class,'product-details')]/div/div/a/following-sibling::div/div[@class='pagination-wrapper']/div/span/img/@src").extract()
            print(images)
            for image in images:
                imageUrls.append(str(image).replace('fullBthumb', '750x922'))
            return imageUrls

    def GetDescription(self, response):
        description = productjson['webLongDescription']
        return description

    def IgnoreProduct(self, response):
        if re.search('"availability":', response.text):
            productAvailability = response.text.split('"availability":')[1].split(',')[0].strip()
            print('productAvailability:', productAvailability)
            if not 'InStock' in productAvailability:
                return True
            else:
                return False

    def GetSizes(self, response):
        productSizes = []
        gender = ProductFilters.objects.get(ProductUrl=GetterSetter.ProductUrl).ParentCategory.split(',')[0]
        for colors in productjson['skucolors']['colors']:
            colorName = colors['colorName']
            for size in colors['skusizes']['sizes']:
                available = size['available']
                sizeName = size['sizeAbbr']
                # fitType = GetFitType(gender, sizeName)
                fitType = productjson['sizeType']
                sizelist = str(colorName), str(sizeName), available, str(fitType), 0.0, 0.0
                productSizes.append(sizelist)
        return productSizes

    def GetCategory(self, response):
        siteMapCategory = str(Spider_BaseClass.ProductUrlsAndCategory.get(GetterSetter.ProductUrl)).replace('None', '')
        return 'Women ' + siteMapCategory
