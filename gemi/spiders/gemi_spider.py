# -*- coding: utf-8 -*-
import scrapy
import re
from urllib.parse import urlencode
from collections import OrderedDict


class GemiSpider(scrapy.Spider):
    name = 'gemi'
    allowed_domains = ['yachtworld.com']

    # Configure item pipelines
    # See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
    custom_settings = {
        'ITEM_PIPELINES': {
            'gemi.pipelines.MongoPipeline': 300,  # pipeline with smaller number executed first
        }
    }

    def generate_search_urls(self):

        search_urls = []
        base_url = 'https://www.yachtworld.com/core/listing/cache/searchResults.jsp'

        https: // www.yachtworld.com / core / listing / cache / searchResults.jsp?cit = true & slim = quick & ybw = & sm = 3 & searchtype = advancedsearch & Ntk = boatsEN & Ntt = & is =true & man = & ftid = 101 & enid = 101 &  & city = & pbsint = & boatsAddedSelected = -1

        # default query
        fromLength = 25
        fromYear = 1995
        fromPrice = 20000
        toPrice = 8000000
        luom = 126 # units feet, meter=127
        currencyid = 100 # US dollar

        # dynamic query
        hull_materials ={'aliminum': 100, 'composite':101, 'fiberglass':102,
                         'steel':103, 'wood': 104,'other':105, 'hypalon':106,
                         'pvc':107, 'ferro-cement':108, 'carbon-fiber':110}
        fuels = {'gas': 100, 'diesel':101, 'other':102}
        number_of_engines = {1:100, 2: 101, 'other':102 , 'none':103 }
        is_new = [True, False]

        recently = {1:1535580789155, 3:1535407989155 , 7:1535062389155 ,14:1534457589155, 30:1533075189155, 60:1530483189155}

        for day in recently:
            for status in is_new:
                for material in hull_materials:
                    for fuel in fuels:
                        for engine_number in number_of_engines:
                            self.active_days = day
                            self.is_new = status
                            self.material = material
                            self.fuel = fuel
                            self.number_of_engines = engine_number

                            search_query = {'fromLength':fromLength,
                                            'fromPrice':fromPrice,
                                            'toPrice':toPrice,
                                            'luom': luom, # unit id
                                            'currencyId': currencyid,
                                            'is': status, # is new
                                            'hmid':material,
                                            'ftid':fuel,
                                            'enid':engine_number,
                                            'pbsint': day,
                                            'ps':100 # entries per page
                                            }
                            search_url = urlencode(OrderedDict(data=base_url, search=search_query))
                            search_urls.append(search_url)

        return search_urls



    def __init__(self, next_page=False,  *args, **kwargs):
        super(GemiSpider, self).__init__(*args, **kwargs)
        self.urls = self.generate_search_urls()
        self.next_page = next_page

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, meta={'dont_redirect': True}, callback=self.parse)

    def parse(self, response):
        SEARCH_RESULTS_SELECTOR = 'div#searchResultsDetailsABTest'
        result_count_selector = 'div.searchResultsCount--mobile-container__searchResultsCount'
        link_selector = 'div.make-model a::attr(href)'
        LENGTH_SELECTOR = 'div.make-model a span.length::text'
        PRICE_SELECTOR = 'div.price::text'
        LOCATION_SELECTOR = 'div.location::text'
        BROKER_SELECTOR = 'div.broker::text'

        ads = response.css(SEARCH_RESULTS_SELECTOR)

        for ad in ads:

            lengths = ad.css(LENGTH_SELECTOR).extract()
            links = ad.css(LINK_SELECTOR).extract()
            prices = ad.css(PRICE_SELECTOR).extract()
            locations = ad.css(LOCATION_SELECTOR).extract()
            brokers = ad.css(BROKER_SELECTOR).extract()

            # remove empty prices
            for i, price in enumerate(prices):
                clean_price = price.replace('\n', '').strip()
                if clean_price == '':
                    prices.pop(i)

            ''' sales pending feature
            ACTIVE_FIELD_SELECTOR = 'div.make-model span.active_field::text'
            statuses = ad.css(ACTIVE_FIELD_SELECTOR).extract()
            if statuses is not None:
                self.logger.info(statuses)  
            '''


            # iterate through items
            for length, link, price, location, broker in zip(lengths, links, prices, locations, brokers):
                # clean the fields
                split_link = link.split('/')
                year, model = split_link[2], split_link[3]
                price = " ".join(price.split())
                length = " ".join(length.split())
                location = " ".join(location.split())
                broker = " ".join(broker.split())


                # send the item to the pipeline
                yield {
                    'model': model,
                    'year': year,
                    'length': length,
                    'price': price,
                    'location': location,
                    'broker': broker,
                    'link': link
                }

        if self.next_page == True:
            next_button = response.css('div.searchResultsNav a.navNext::attr(href)').extract_first()
            if next_button is not None:
                yield response.follow(next_button, callback=self.parse)