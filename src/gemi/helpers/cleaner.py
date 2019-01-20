import re


def clean_price(price):
    price = " ".join(price.split())
    price = remove_messy_chars(price)
    if price.isdigit():
        price = int(price)
    return price


def remove_messy_chars(dirty_string):
    messy_chars = {'US$', ',', '(', ')', '⁄', ' ', '\n', '\t', '[', ']'}
    for ch in messy_chars:
        if ch in dirty_string:
            dirty_string = dirty_string.replace(ch, '')
    return dirty_string


def remove_digits(word):
    return re.sub("\d+", "", word)


def remove_non_alpha_numeric_chars(word):
    return re.sub("[^\w]", "", word)
