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
    # entry point
    def __init__(self, next_page=False, *args, **kwargs):
        super(GemiSpider, self).__init__(*args, **kwargs)
        self.urls, self.extra_info = GemiUtil.generate_search_urls_and_extra_info()
        self.next_page = next_page


    def start_requests(self):
        for url, extra_info_for_query in zip(self.urls, self.extra_info):
            yield scrapy.Request(url=url,
                                 meta={'extra_info': extra_info_for_query},
                                 callback=self.parse)



    def parse(self, response):
        # selectors
        search_results_table_selector = 'div#searchResultsDetailsABTest'
        result_count_selector = 'div.searchResultsCount--mobile-container__searchResultsCount'

        # define the data to process
        search_results = response.css(search_results_table_selector)
        result_count = response.css(result_count_selector).extract()
        extra_info = response.meta['extra_info']

        self.process_search_results(search_results, extra_info)

        # follow to the next page
        if self.next_page == True:
            next_button = response.css('div.searchResultsNav a.navNext::attr(href)').extract_first()
            if next_button is not None:
                yield response.follow(next_button, callback=self.parse)


    def process_search_results(self, search_results, extra_info):
        link_selector = 'div.make-model a::attr(href)'
        length_selector = 'div.make-model a span.length::text'
        price_selector = 'div.price::text'
        location_selector = 'div.location::text'
        broker_selector = 'div.broker::text'
        sales_status_selector = 'div.make-model span.active_field::text'

        ''' sales pending feature
        ACTIVE_FIELD_SELECTOR = 'div.make-model span.active_field::text'
        statuses = ad.css(ACTIVE_FIELD_SELECTOR).extract()
        if statuses is not None:
            self.logger.info(statuses)  
        '''

        for ad in search_results:
            lengths = ad.css(length_selector).extract()
            links = ad.css(link_selector).extract()
            prices = ad.css(price_selector).extract()
            locations = ad.css(location_selector).extract()
            brokers = ad.css(broker_selector).extract()
            # remove empty prices
            prices = GemiUtil.remove_empty_prices(prices)

            self.process_items(lengths, links, prices, locations, brokers, extra_info)

    def process_items(self,lengths, links, prices, locations, brokers, extra_info)
        # iterate through items
        for length, link, price, location, broker in zip(lengths, links, prices, locations, brokers):

            # get the year and model from the link
            split_link = link.split('/')
            year, model = split_link[2], split_link[3]

            # clean the fields
            cleaned_fields = list(map(lambda field: " ".join(field.split()), [price, length, location, broker]))
            price, length, location, broker = cleaned_fields


            # send the item to the pipeline
            yield {
                'model': model,
                'year': year,
                'length': length,
                'price': price,
                'location': location,
                'broker': broker,
                'link': link,
                'is_new': extra_info['new_or_used'],
                'active_days': extra_info['day'],
                'material': extra_info['material'],
                'fuel': extra_info['fuel'],
                'number of engines': extra_info['engine_number']
            }


class GemiUtil(object):

    @staticmethod
    def remove_empty_prices(prices):
        for i, price in enumerate(prices):
            clean_price = price.replace('\n', '').strip()
            if clean_price == '':
                prices.pop(i)
        return prices

    @staticmethod
    def generate_search_urls_and_extra_info():
        # initialize
        search_urls = []
        extras = []
        base_url = 'https://www.yachtworld.com/core/listing/cache/searchResults.jsp'

        # default query
        fromLength = 25
        fromYear = 1995
        fromPrice = 20000
        toPrice = 8000000
        luom = 126  # units feet, meter=127
        currencyid = 100  # US dollar

        # dynamic query parameters
        hull_materials = {'aliminum': 100, 'composite': 101, 'fiberglass': 102,
                          'steel': 103, 'wood': 104, 'other': 105, 'hypalon': 106,
                          'pvc': 107, 'ferro-cement': 108, 'carbon-fiber': 110}
        fuels = {'gas': 100, 'diesel': 101, 'other': 102}
        number_of_engines = {1: 100, 2: 101, 'other': 102, 'none': 103}
        is_new = [True, False]
        recently = {1: 1535580789155, 3: 1535407989155, 7: 1535062389155, 14: 1534457589155, 30: 1533075189155,
                    60: 1530483189155}

        # generate dynamic queries
        for recent_day in recently:
            for new_or_used in is_new:
                for material in hull_materials:
                    for fuel in fuels:
                        for engine_number in number_of_engines:
                            extra_info = {'days': recent_day, 'is_new': status,
                                          'material': material, 'fuel': fuel, 'number_of_engines': engine_number}

                            search_query = {'fromLength': fromLength,
                                            'fromYear': fromYear,
                                            'fromPrice': fromPrice,
                                            'toPrice': toPrice,
                                            'luom': luom,  # unit id
                                            'currencyId': currencyid,
                                            'is': new_or_used,
                                            'hmid': material,
                                            'ftid': fuel,
                                            'enid': engine_number,
                                            'pbsint': recent_day,
                                            'ps': 100  # entries per page
                                            }

                            search_url = urlencode(OrderedDict(data=base_url, search=search_query))
                            search_urls.append(search_url)
                            extras.append(extra_info)

        return search_urls, extras