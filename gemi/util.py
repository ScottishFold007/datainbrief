

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


    @staticmethod
    def check_price_change(item, price):
        price_list = item['price_list']
        last_price = price_list[-1][0]  # get the value of the last price (price,time) tuples
        if last_price != price:
            date = datetime.datetime.now().date()
            new_price = (price, date)
            price_list.append(new_price)

        return item
