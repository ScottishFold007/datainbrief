from src.db.credentials import db
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne
import re
from tqdm import tqdm

query = {'details.loa': {"$exists": True}}
cursor = db.boats.find(query, snapshot=True).count()


def bulk_exec(ops):
    try:
        db.boats.bulk_write(ops, ordered=False)
        ops = []
        return ops
    except BulkWriteError as bwe:
        print(bwe.details)


def bulk_base():
    ops = []

    for doc in tqdm(cursor):
        query = {'_id': doc['_id']}
        updates = dict()

        if updates:
            new_update = UpdateOne(query, {'$set': updates})
            ops.append(new_update)

        if len(ops) >= 10000:
            ops = bulk_exec(ops)

    if ops:
        bulk_exec(ops)


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

