
class Cleaner:
    @staticmethod
    def remove_empty_chars_and_new_lines(fields):
        # clean the fields
        cleaned_fields = list(map(lambda field: " ".join(field.split()), fields))
        return cleaned_fields

    @staticmethod
    def remove_empty_prices(prices):
        for i, price in enumerate(prices):
            clean_price = price.replace('\n', '').strip()
            if clean_price == '':
                prices.pop(i)
        return prices

    @staticmethod
    def clean_price(price):
        price = " ".join(price.split())
        messy_chars = {'US$', ',', '(', ')', '⁄', ' ', '\n', '\t', '[', ']'}

        for ch in messy_chars:
            if ch in price:
                price = price.replace(ch, '')

        if price.isdigit():
            price = int(price)

        return price
