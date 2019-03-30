from src.db import db
from scrapy import Request, Spider
from enum import Enum


class Selectors(Enum):
    full_spec_selector = 'div.fullspecs div:first-child::text'


class DetailSpider(Spider):
    name = 'details'

    custom_settings = {
        'ITEM_PIPELINES': {
            'src.pipelines.DetailPipeline': 200,
        }
    }

    def __init__(self, *args, **kwargs):
        super(DetailSpider, self).__init__(*args, **kwargs)
        self.start_urls = db.get_items_without_details()

    # Send urls to parse
    def start_requests(self):
        for url in self.start_urls:
            if 'http' not in url:
                continue
            yield Request(url=url, meta={'url': url}, callback=self.parse)

    @staticmethod
    def get_specs(full_specs):
        specs = dict()
        for line in full_specs:
            line = " ".join(line.split()).lower()
            line = line.split(':')
            if len(line) == 2:
                spec_key = " ".join(line[0].split())
                spec_key.replace(' ', '_')
                spec_value = " ".join(line[1].split())
                if spec_key == 'engine_hours':
                    spec_value = int(spec_value)
                specs[spec_key] = spec_value
            else:
                continue

        return specs

    def parse(self, response):
        full_specs = response.css(Selectors.full_spec_selector).extract()
        item_link = response.meta['url']
        specs = self.get_specs(full_specs)

        yield {
            'link': item_link,
            'details': specs
        }
