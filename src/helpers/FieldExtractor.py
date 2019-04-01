import re


class FieldExtractor(object):
    item_selectors = {
        'length': 'div.make-model a span.length::text',
        'location': 'div.location::text',
        'sale_pending': 'div.location span.active_field::text',
        'broker': 'div.broker::text',
        'link': 'div.make-model a::attr(href)',
        'price': 'div.price::text'
    }

    # basic field selectors
    def extract_item(self, row):
        item = dict()
        for field_key, selector in self.item_selectors.items():
            try:
                field_value = row.css(selector).extract_first()
                if field_value:
                    field_value = " ".join(field_value.split())
                    if field_key == 'length':
                        field_value = int(re.findall(r'\d+', field_value)[0])
                else:
                    field_value = ""
            except TypeError:
                field_value = ""
            item[field_key] = field_value
        return item

    @staticmethod
    def get_maker_model_and_year(link):
        # get the year and model from the link
        base_url = 'https://www.yachtworld.com'
        sub_link = link.replace(base_url, '')
        split_link = sub_link.split('/')
        year, model = split_link[2], split_link[3]
        model = model.split('-')
        # the last element is irrelevant
        model = " ".join(model[:-1]).lower()
        return {
            'model': model,
            'year': int(year)
        }

    @staticmethod
    def extract_city_state_and_country_from_location(location):
        state = ""
        location_parts = location.split(',')
        country = location_parts[-1]
        city = location_parts[0]
        if len(location_parts) == 3:
            state = location_parts[2]
        return {
            'city': city,
            'state': state,
            'country': country
        }
