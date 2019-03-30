from scrapy import Spider
from abc import ABC, abstractmethod



class AbstractSpider(ABC, Spider):

    @property
    def name(self):
        raise NotImplementedError

    @property
    def base_url(self):
        raise NotImplementedError

    @property
    def allowed_domains(self):
        raise NotImplementedError

    @property
    def start_urls(self):
        raise NotImplementedError

    @property
    def next_page(self):
        raise NotImplementedError

    @abstractmethod
    def __init__(self, *args, **kwargs):
        super(AbstractSpider, self).__init__(*args, **kwargs)

    @abstractmethod
    def start_requests(self):
        pass

    @abstractmethod
    def parse(self, response):
        pass



class BaseSpider(AbstractSpider):
    def parse(self, response):
        name = ''
        start_urls = list()
        base_url = ''
        allowed_domains = list()
        next_page = True
        custom_settings = {
            'ITEM_PIPELINES': {
            }
        }

        data_selector = ''
        data = response.css(data_selector)
        for page in data:
            yield None

        if self.next_page:
            yield response.follow(self.next_page, callback=self.parse)
