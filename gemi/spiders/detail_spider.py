# -*- coding: utf-8 -*-
# packages
import scrapy
from gemi.database import get_db
import gemi.detail_spider_processors.detail_processor as processor


class DetailSpider(scrapy.Spider):
    name = 'detail'
    allowed_domains = ['yachtworld.com']

    custom_settings = {
        'ITEM_PIPELINES': {
            'gemi.pipelines.DuplicatesPipeline': 200,
            'gemi.pipelines.DetailPipeline': 300  # pipeline with smaller number executed first
        }
    }

    # entry point
    def __init__(self,*args, **kwargs):
        super(DetailSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://www.yachtworld.com'
        self.start_urls = self.get_detail_links()
        self.db = get_db()

    def get_detail_links(self):
        links = self.db.yachts.distinct('link')
        urls = list()
        for link in links:
            if 'http' in link: # already ok
                continue
            url = self.base_url + link
            urls.append(url)
        return urls

    # Send urls to parse
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        detail_selector = 'div.boatdetails::text'
        detail = response.css(detail_selector).extract()
        hours = processor.get_hours(detail)
        item= dict()
        item.update({'hours': hours})
        if hours == 'hour in description':
            detail = " ".join(detail.split())
            item.update({'detail': detail})
        # send the item info to the pipeline
        yield item
