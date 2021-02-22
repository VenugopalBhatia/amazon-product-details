from scrapy.spiders import Spider
import scrapy
from scrapy.loader import ItemLoader
from brandAsinMap.items import BrandasinmapItem
from datetime import datetime
from scrapy_selenium import SeleniumRequest

class BrandAsinSpider(Spider):

    name = 'brandMapping'
    allowed_domains = ["amazon.in"]

    def __init__(self,**kwargs):
        # self.asinList = kwargs['asins']
        self.asinList =  ['B00LJWFA44','B00LJWFAOY']
        self.errAsins = []

    

    def start_requests(self):
        
        for asin in self.asinList:
            
            request =  SeleniumRequest(url = "https://www.amazon.in/dp/{}".format(asin), callback = self.parseData,errback=self.asinsNotScraped)
            request.meta['asin'] = asin
            request.meta['proxy'] = "172.16.115.110:25008"
            yield request
            

    def asinsNotScraped(self,err):
        self.logger.error(err)
        self.errAsins.append(err.request.meta['asin'])

    
    def parseData(self,response):
        if self.check_blocked(response):
            return
        asin = response.request.meta.get('asin')
        product = ItemLoader(item = BrandasinmapItem(),response=response)
        # product['brand'] = response.css('#bylineInfo::text').get()
        # product['title'] = response.css('#productTitle::text').get()
        # product['asin'] = asin
        product.add_value('brand',response.css('#bylineInfo::text').get())
        product.add_value('title',response.css('#productTitle::text').get())
        product.add_value('asin',asin)

        product.add_xpath('title', '//span[@id="productTitle"]/text()')
        product.add_xpath('manufacturer', '//a[@id="bylineInfo"]/text()')
        product.add_xpath('rating', '//div[@id="averageCustomerReviews"]//span[@id="acrPopover"]/@title')
        product.add_xpath('rating_count', '//div[@id="averageCustomerReviews"]//span[@id="acrCustomerReviewText"]/text()[normalize-space(.)]')
        product.add_xpath('answered_questions', '//a[@id="askATFLink"]/span/text()[normalize-space(.)]')
        product.add_xpath('promote', '//div[@data-feature-name="acBadge"]//span//text()[normalize-space(.)]')
        product.add_xpath('mrp', '//*[@id="price"]/table/tbody/tr[1]/td[2]/span[1]/text()')
        product.add_xpath('price', '//*[@id="priceblock_ourprice" or @id="priceblock_dealprice"]//text()')
        product.add_xpath('categories', '//*[@id="wayfinding-breadcrumbs_container"]//li[not(contains(@class, "a-breadcrumb-divider"))]/span//text()')
        if response.css('.fbaBadge'):
            product.add_value('fba', True)
        offers = []
        print(response.css('.sopp-offer-enumerator').xpath('following-sibling::div'))
        for offer in response.css('.sopp-offer-enumerator').xpath('./following-sibling::div'):
            name = offer.xpath('.//*[@aria-hidden="true"]').css('.sopp-offer-title').xpath('.//text()').get()
            description = offer.xpath('.//*[@aria-hidden="true"]').css('.description').xpath('.//text()').extract()
            if not name == None:
                offers.append(
                    {
                        name: ''.join(description)
                    }
                )
        product.add_value('offers', offers)
        # product.add_xpath('offers', '//*[@class="sopp-offer-title"]/../span/text()[normalize-space(.)]')
        product.add_xpath('extra_features', '//*[@id="icon-farm-container"]/div/div/div[2]//text()[normalize-space(.)]')
        product.add_xpath('expiry_date', '//*[@data-feature-name="expiryDate"]//text()')
        product.add_xpath('availability', '//*[@id="availability"]//text()')
        product.add_xpath('merchant_info', '//*[@id="merchant-info"]//text()')
        product.add_xpath('olp', '//*[@data-feature-name="olp"]//text()')
        styles = []
        index = 0
        for style in response.xpath('//*[@data-feature-name="twister"]//ul/li'):
            name = style.xpath('./@title').get()
            asin = style.xpath('./@data-defaultasin').get()
            price = style.xpath(f'.//*[@id="style_name_{index}_price" or @id="pattern_name_{index}_price"]/span/text()').get()
            style_item = {
                "name": name,
                "asin": asin,
                "price": price
            }

            styles.append(style_item)
            index += 1
        product.add_value('styles', styles)
        product.add_xpath('design', '//*[@id="variation_pattern_name"]/div/span/text()')
        product.add_xpath('features', '//*[@data-feature-name="featurebullets"]//ul/li//text()')
        bsr_selector = response.xpath("//*[@id='SalesRank']//text()[not(parent::style)][normalize-space(.)]")
        
        if bsr_selector:
            bsr = bsr_selector.getall()
        else:
            try:
                bsr_selector = response.xpath("//*[contains(@href,'/gp/bestsellers/')]/ancestor-or-self::*[(contains(.,'Rank') or contains(., 'rank')) and (contains(.,'sellers') or contains(.,'Sellers'))][1]")
                bsr = bsr_selector[-1].xpath('.//text()[not(parent::style)][not(parent::noscript)][not(parent::script)]').getall()
            except:
                bsr = ''

        bsr = "NOT_FOUND" if bsr=='' or bsr is None or (len(bsr)>256) else bsr
        dfa_selector = response.xpath("//*[contains(., 'Date First Available')]")
        if dfa_selector and len(dfa_selector) > 0:
            dfa = dfa_selector[-1].xpath('./..//text()[not(parent::style)][not(parent::noscript)][not(parent::script)]').getall()
        else:
            dfa = None
        dfa = "NOT_FOUND" if dfa=='' or dfa is None or (len(dfa)>256)else dfa
        
        product.add_value('bsr', bsr)
        product.add_value('dfa', dfa)
        product.add_xpath('description', '//*[@id="productDescription"]/p//text()')
        product.add_xpath('aplus_images', '//*[@id="aplus"]//img/@src[not(contains(., "gif"))]')
        product.add_xpath('aplus_text', '//*[@id="aplus"]//*[not(self::style)][not(self::noscript)][not(self::script)]/text()')
        customer_reviews = response.xpath('//*[@id="reviewsMedley"]')

        star_ratings = {}
        print(response.xpath('//*[@id="reviewsMedley"]//table[@id="histogramTable"]'))
        for star_rating in customer_reviews.xpath('.//table[@id="histogramTable"]//tr'):
            star = star_rating.xpath('./td[1]//a/text()[normalize-space(.)]').get()
            percentage = star_rating.xpath('./td[3]//a/text()[normalize-space(.)]').get()
            star_ratings[star] = percentage
        print(star_ratings)
        product.add_value('star_ratings', star_ratings)

        cr_summary = {}
        for summary in customer_reviews.xpath('//*[@id="cr-summarization-attributes-list"]/div'):
            pivot = summary.xpath('.//i')
            attribute = pivot.xpath('./../preceding-sibling::*//span/text()').get()
            rating = pivot.xpath('./span/text()').get()
            cr_summary[attribute] = rating
        product.add_value('cr_summary', cr_summary)
        product.add_value('url', response.request.url)
        
       

        yield product.load_item()


    def check_blocked(self, response):
            page_title = response.xpath('//title/text()').get()
            if page_title == "Robot Check":
                print(
                    "******************Blocked by Amazon**********************")
                return True
            return False

