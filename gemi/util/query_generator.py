from urllib.parse import urlencode
from collections import OrderedDict


class QueryGenerator:
    @staticmethod
    def generate_urls_for_search_queries():
        urls = list()
        root_search_url = 'https://www.yachtworld.com/core/listing/cache/searchResults.jsp'

        # default query
        base_query_parameters = {
            'fromLength': 25,
            'toLength': '',
            'fromYear': 1995,
            'toYear': '',
            'fromPrice': 20000,
            'toPrice': 8000000,
            'luom': 126,  # units feet, meter=127
            'currencyid': 100,  # US dollar
            'ps': 300  # entries per page
        }

        within_x_days = [(1, 1535580789155), (3, 1535407989155), (7, 1535062389155),
                         (14, 1534457589155), (30, 1533075189155), (60, 1530483189155), ('60+', '')]

        within_x_days = OrderedDict(within_x_days)

        # generate queries for all day options
        for day, pbsint in within_x_days.items():
            base_query_parameters['pbsint'] = pbsint
            query_string = urlencode(base_query_parameters, 'utf-8')
            query_url = root_search_url + '?' + query_string
            urls.append(query_url)

        return urls
