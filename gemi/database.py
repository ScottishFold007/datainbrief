from pymongo import MongoClient

client = MongoClient(host='mongodb://<dbuser>:<dbpassword>@ds237072.mlab.com:37072/gemi',
                     port=47450,
                     username='roxy',
                     password='gemicik1',
                     authSource='gemi',
                     authMechanism='SCRAM-SHA-1')

db_name = 'gemi'
db = client[db_name]

