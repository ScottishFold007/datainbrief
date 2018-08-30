# -*- coding: utf-8 -*-
import scrapy
import re


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

    def __init__(self, urls, next_page=False,  *args, **kwargs):
        super(GemiSpider, self).__init__(*args, **kwargs)
        self.urls = [urls]
        self.next_page = next_page
        self.base_url = 'https://www.yachtworld.com'

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, meta={'dont_redirect': True}, callback=self.parse)

    def parse(self, response):
        SEARCH_RESULTS_SELECTOR = 'div#searchResultsDetailsABTest'
        LINK_SELECTOR = 'div.make-model a::attr(href)'
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