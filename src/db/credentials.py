from pymongo import MongoClient


collection = 'boats'

client = MongoClient(host='mongodb://<dbuser>:<dbpassword>@ds237072.mlab.com:37072/gemi',
                     port=47450,
                     username='roxy',
                     password='gemicik1',
                     authSource='gemi',
                     authMechanism='SCRAM-SHA-1')
db = client['gemi']





