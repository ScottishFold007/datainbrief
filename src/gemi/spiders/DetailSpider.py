from gemi.base.AbstractClasses.AbstractSpider import AbstractSpider
from gemi.BoatsDatabase import boats_database
from scrapy import Request


class DetailSpider(AbstractSpider):
    name = 'boat_details'
    next_page = False
    start_urls = boats_database.get_items_without_details()
    base_url = 'https://www.yachtworld.com'
    allowed_domains = ['yachtworld.com']

    custom_settings = {
        'ITEM_PIPELINES': {
            'gemi.pipelines.DetailPipeline': 200,
        }
    }

    def __init__(self, *args, **kwargs):
        super(DetailSpider, self).__init__(*args, **kwargs)

    # Send urls to parse
    def start_requests(self):
        for url in self.start_urls:
            if 'http' not in url:
                continue
            yield Request(url=url, meta={'url': url}, callback=self.parse)

    def parse(self, response):
        full_spec_selector = 'div.fullspecs div:first-child::text'
        full_specs = response.css(full_spec_selector).extract()
        item_link = response.meta['url']

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

        yield {
            'link': item_link,
            'details': specs
        }
