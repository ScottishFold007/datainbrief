from src.db.credentials import db
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne
import re
from tqdm import tqdm

cursor = db.boats.find({}, snapshot=True)


def bulk_exec(ops):
    try:
        db.boats.bulk_write(ops, ordered=False)
        ops = []
        return ops
    except BulkWriteError as bwe:
        print(bwe.details)


def old():
    def get_hours(doc):
        details = doc.get('details')
        if details and isinstance(details, dict) and 'engine_hours' in details:
            hours = details['engine_hours']
            if hours:
                return int(hours)

    def get_length(doc):
        length = doc.get('length')

        if not length:
            return None

        length = re.findall(r'\d+', str(length))[0]
        return int(length)

    def update_db():
        ops = []

        for doc in tqdm(cursor):
            query = {'_id': doc['_id']}
            updates = dict()

            lows = ['model', 'country', 'broker']

            if doc.get(lows[0]).islower() and doc.get(lows[1]).islower() and doc.get(lows[2]).islower():
                continue

            for low in lows:
                updates[low] = doc.get(low).strip().lower()

            new_update = UpdateOne(query, {'$set': updates})
            ops.append(new_update)

            if len(ops) >= 10000:
                ops = bulk_exec(ops)

        if ops:
            bulk_exec(ops)

    def old_update():
        ops = []

        for doc in tqdm(cursor):
            query = {'_id': doc['_id']}
            updates = dict()

            price = doc['price']

            if isinstance(price, list):
                updates['price'] = price.pop()

            try:
                updates['year'] = int(doc.get('year'))
            except TypeError:
                pass

            hours = get_hours(doc)
            if hours:
                updates['hours'] = hours

            length = get_length(doc)
            if length:
                updates['length'] = hours

            if updates:
                new_update = UpdateOne(query, {'$set': updates})
                ops.append(new_update)

            if len(ops) >= 10000:
                ops = bulk_exec(ops)

        if ops:
            bulk_exec(ops)
