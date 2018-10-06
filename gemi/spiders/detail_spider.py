# -*- coding: utf-8 -*-
# packages
import scrapy
from gemi.pipelines import DetailPipeline


class DetailSpider(scrapy.Spider):
    name = 'detail'
    allowed_domains = ['yachtworld.com']
    base_url = 'https://www.yachtworld.com'
    custom_settings = {
        'ITEM_PIPELINES' : {
           # 'gemi.pipelines.DetailPipeline': 200, # the number in range 0-1000
        }
    }
    # entry point
    def __init__(self, *args, **kwargs):
        super(DetailSpider, self).__init__(*args, **kwargs)
        self.start_urls = DetailPipeline.get_links()

    # Send urls to parse
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, meta={'url': url}, callback=self.parse)

    def parse(self, response):
        fullspec_selector = 'div.fullspecs div:first-child::text'
        fullspecs = response.css(fullspec_selector).extract()
        hour_in_various_languages = {'hour', 'time', 'stunde', 'ora', 'heure', 'uur', 'tunnin', 'timme', 'saat',
                                     'hora'}
        hours = list()
        for line in fullspecs:
            line = " ".join(line.split()).lower()
            if any(word in line for word in hour_in_various_languages):
                hours.append(line)

        # link = response.meta['url']

        item = {'hours':hours}

        # send the item info to the pipeline
        yield item
