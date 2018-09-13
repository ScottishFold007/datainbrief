

class GemiUtil(object):
    @staticmethod
    def remove_empty_prices(prices):
        for i, price in enumerate(prices):
            clean_price = price.replace('\n', '').strip()
            if clean_price == '':
                prices.pop(i)
        return prices

    @staticmethod
    def extract_hours_from_details(details):
        if 'hours' in details:
            pass
        else:
            return 'no hour info in details'
