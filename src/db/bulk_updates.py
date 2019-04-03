from src.db.credentials import db
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne
import re
from tqdm import tqdm

query = {'details.loa': {"$exists": True}}
cursor = db.boats.find(query, snapshot=True)


# length = re.findall(r'\d+', str(length))[0]


def bulk_exec(ops):
    try:
        db.boats.bulk_write(ops, ordered=False)
        ops = []
        return ops
    except BulkWriteError as bwe:
        print(bwe.details)


def get_updates(doc):
    loa = doc['details']['loa']

    length = loa.split()[0]

    return float(length)


def bulk_base():
    ops = []

    for doc in tqdm(cursor):
        query = {'_id': doc['_id']}
        updates = dict()

        updates = get_updates()

        if updates:
            new_update = UpdateOne(query, {'$set': updates})
            ops.append(new_update)

        if len(ops) >= 10000:
            ops = bulk_exec(ops)

    if ops:
        bulk_exec(ops)


def test():
    for doc in tqdm(cursor):
        print(get_updates(doc))
