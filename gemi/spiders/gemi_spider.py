# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urlencode
from collections import OrderedDict
from itertools import product


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
    def __init__(self, next_page=False, details=False *args, **kwargs):
        super(GemiSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://www.yachtworld.com'
        self.urls = GemiUtil.generate_base_query_url()
        self.next_page = next_page
        self.should_get_details = details


    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url,
                                 callback=self.parse)



    def parse(self, response):
        # selectors
        search_results_table_selector = 'div#searchResultsDetailsABTest'
        result_count_selector = 'div.searchResultsCount--mobile-container__searchResultsCount'

        # define the data to process
        search_results = response.css(search_results_table_selector)
        result_count = response.css(result_count_selector).extract()

        self.process_search_results(search_results)

        # follow to the next page
        if self.next_page:
            next_button = response.css('div.searchResultsNav a.navNext::attr(href)').extract_first()
            if next_button is not None:
                yield response.follow(next_button, callback=self.parse)


    def process_search_results(self, search_results):
        for page in search_results:
            lengths, links, prices, locations, brokers = self.extract_ads(page)
            self.process_items(lengths, links, prices, locations, brokers)


    def extract_ads(self, page):
        link_selector = 'div.make-model a::attr(href)'
        length_selector = 'div.make-model a span.length::text'
        price_selector = 'div.price::text'
        location_selector = 'div.location::text'
        broker_selector = 'div.broker::text'

        lengths = page.css(length_selector).extract()
        links = page.css(link_selector).extract()
        prices = page.css(price_selector).extract()
        locations = page.css(location_selector).extract()
        brokers = page.css(broker_selector).extract()
        # remove empty prices
        prices = GemiUtil.remove_empty_prices(prices)

        return lengths, links, prices, locations, brokers



    def process_items(self,lengths, links, prices, locations, brokers):
        # iterate through items
        for length, link, price, location, broker in zip(lengths, links, prices, locations, brokers):
            

            # get the year and model from the link
            split_link = link.split('/')
            year, model = split_link[2], split_link[3]

            # clean the fields
            cleaned_fields = list(map(lambda field: " ".join(field.split()), [price, length, location, broker]))
            price, length, location, broker = cleaned_fields

             
            # make the link clickable
            link = self.base_url + link

            # go to the item page to get details
            if self.should_get_details == True:

                # send a request to the details page
                yield scrapy.Request(
                    link, 
                    callback = self.parseCoordinates,
                    meta = {
                            'model': model,
                            'year': year,
                            'length': length,
                            'price': price,
                            'location': location,
                            'broker': broker,
                            'link': link
                    }
                )
            else: 
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
            





class GemiUtil(object):

    @staticmethod
    def remove_empty_prices(prices):
        for i, price in enumerate(prices):
            clean_price = price.replace('\n', '').strip()
            if clean_price == '':
                prices.pop(i)
        return prices

    @staticmethod
    def generate_base_query_url():
        base_url = 'https://www.yachtworld.com/core/listing/cache/searchResults.jsp'

        # default query
        fromLength = 25
        fromYear = 1995
        fromPrice = 20000
        toPrice = 8000000
        luom = 126  # units feet, meter=127
        currencyid = 100  # US dollar

        base_query = {
                        'fromLength': fromLength,
                        'fromYear': fromYear,
                        'fromPrice': fromPrice,
                        'toPrice': toPrice,
                        'luom': luom,  # unit id
                        'currencyId': currencyid,
                        'ps': 100  # entries per page

                    }

        base_query_url = urlencode(OrderedDict(data=base_url, search=base_query))

        return list(base_query_url)



    # LATER
    @staticmethod # broken, take a look
    def generate_search_urls_and_extra_info():
        # initialize
        search_urls = []
        extras = []


        # dynamic query parameters
        hull_materials = {'aluminium': 100, 'composite': 101, 'fiberglass': 102,
                          'steel': 103, 'wood': 104, 'other': 105, 'hypalon': 106,
                          'pvc': 107, 'ferro-cement': 108, 'carbon-fiber': 110}
        fuels = {'gas': 100, 'diesel': 101, 'other': 102}
        number_of_engines = {1: 100, 2: 101, 'other': 102, 'none': 103}
        is_new = [True, False]
        within_x_days = {1: 1535580789155, 3: 1535407989155, 7: 1535062389155, 14: 1534457589155, 30: 1533075189155,
                    60: 1530483189155}
        recent_day = new_or_used = material = fuel = engine_number = 'unknown'

        if daily_search:
            within_x_days = {1: 1535580789155 }


        # generate dynamic queries
        for recent_day, new_or_used, material, fuel, engine_number in product(
                within_x_days, is_new, hull_materials,
                fuels, number_of_engines):

            extra_info = {'days': recent_day, 'is_new': new_or_used,
                          'material': material, 'fuel': fuel, 'number_of_engines': engine_number}

            detailed_query = {
                            'is': new_or_used,
                            'hmid': material,
                            'ftid': fuel,
                            'enid': engine_number,
                            'pbsint': recent_day,
                            }

            search_url = urlencode(OrderedDict(data=base_url, search=search_query))
            search_urls.append(search_url)
            extras.append(extra_info)

        return search_urls, extras