from src.helpers.db import db
from scrapy import Request, Spider


class DetailSpider(Spider):
    name = 'details'

    custom_settings = {
        'ITEM_PIPELINES': {
            'src.helpers.pipelines.DetailPipeline': 200,
        }
    }

    full_spec_selector = 'div.fullspecs div:first-child::text'

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
    def get_details(full_specs):
        details = dict()
        for line in full_specs:
            line = " ".join(line.split()).lower()
            line = line.split(':')
            if len(line) == 2:
                detail_key = " ".join(line[0].split())
                detail_key.replace(' ', '_')
                detail_value = " ".join(line[1].split())
                if detail_key == 'engine_hours':
                    detail_value = int(detail_value)
                details[detail_key] = detail_value
            else:
                continue

        return details

    def parse(self, response):
        full_specs = response.css(self.full_spec_selector).extract()
        item_link = response.meta['url']
        details = self.get_details(full_specs)

        yield {
            'link': item_link,
            'details': details
        }
