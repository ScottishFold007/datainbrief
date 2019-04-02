from src.db.credentials import db, collection
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne
import re

cursor = db.boats.find({"$snapshot": True})
ops = list()


def get_hours(doc):
    try:
        details = doc['details']
        if details and isinstance(details, dict) and 'engine_hours' in details:
            hours = details['engine_hours']
            if hours:
                return hours
    except KeyError as e:
        return None


def get_length(doc):
    try:
        length = doc['length']
        length = re.findall(r'\d+', str(length))[0]
        return int(length)

    except KeyError as e:
        return None


for doc in cursor:
    query = {'_id': doc['_id']}
    updates = dict()

    price = doc['price']

    if isinstance(price, list):
        updates['price'] = price.pop()

    try:
        updates['year'] = int(doc['year'])
    except TypeError:
        pass

    hours = get_hours(doc)
    if hours:
        updates['hours'] = hours

    length = get_length(doc)
    if length:
        updates['length'] = hours

    lows = ['model', 'country', 'broker']
    for low in lows:
        updates[low] = doc[low].strip().lower()

    new_update = UpdateOne(query, {'$set': updates})
    ops.append(new_update)

    if len(ops) >= 1000:
        try:
            db.boats.bulk_write(ops, ordered=False)
            ops = []
        except BulkWriteError as bwe:
            print(bwe.details)
