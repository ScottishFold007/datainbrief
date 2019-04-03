from src.db.credentials import db
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne
import re
from tqdm import tqdm


query = {'details.total power': {"$exists": True}}
cursor = db.boats.find(query, snapshot=True)

makers = ['absolute', 'astondoa', 'azimut', 'bavaria', 'bayliner', 'beneteau', 'benetti', 'bennington', 'bertram', 'boston whaler', 'c&c', 'cabo', 'carver', 'catalina', 'chaparral', 'chris-craft', 'cobalt', 'cobia', 'contender', 'cranchi', 'crest', 'crownline', 'cruisers yachts', 'custom', 'dufour', 'edgewater', 'elan', 'everglades', 'fairline', 'ferretti yachts', 'formula', 'fountain', 'fountaine pajot', 'four winns', 'galeon', 'grady-white', 'grand banks', 'grand soleil', 'hallberg-rassy', 'hanse', 'harris', 'hatteras', 'hinckley', 'hunter', 'intrepid', 'island packet', 'j boats', 'jeanneau', 'key west', 'lagoon', 'larson', 'leopard', 'luhrs', 'mainship', 'maiora', 'mako', 'mangusta', 'mastercraft', 'maxum', 'meridian', 'monterey', 'moody', 'nauticstar', 'nautique', 'ocean alexander', 'ocean yachts', 'pearson', 'pershing', 'prestige', 'princess', 'pursuit', 'ranger tugs', 'regal', 'regulator', 'rinker', 'riva', 'riviera', 'robalo', 'rodman', 'sabre', 'sailfish', 'sanlorenzo', 'scout', 'sea fox', 'sea hunt', 'sea ray', 'sealine', 'sessa', 'silverton', 'sportsman', 'sunseeker', 'tahoe', 'tartan', 'tiara', 'viking', 'wellcraft', 'westerly', 'x-yachts', 'yamaha boats', 'zodiac']

# length = re.findall(r'\d+', str(length))[0]


def bulk_exec(ops):
    try:
        db.boats.bulk_write(ops, ordered=False)
    except BulkWriteError as bwe:
        print(bwe.details)


def get_maker(doc):
    updates = dict()



    return updates


def bulk_update():
    ops = []

    for doc in tqdm(cursor):
        id_query = {'_id': doc['_id']}

        updates = get_maker(doc)

        if updates:
            new_update = UpdateOne(id_query, {'$set': updates})
            ops.append(new_update)

        if len(ops) >= 4200:
            bulk_exec(ops)
            ops = []

    if ops:
        bulk_exec(ops)


def test():
    for doc in tqdm(cursor):
        print(get_updates(doc))
