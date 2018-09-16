from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING, TEXT


class Database(object):
    def __index__(self):
        self.client = self.get_db_client()
        self.db = self.client['gemi']  # db name

        return self.client, self.db

    @staticmethod
    def get_db_client():
        client = MongoClient(host='mongodb://<dbuser>:<dbpassword>@ds237072.mlab.com:37072/gemi',
                             port=47450,
                             username='roxy',
                             password='gemicik1',
                             authSource='gemi',
                             authMechanism='SCRAM-SHA-1')

        return client

    def remove_duplicates(self):
        print('removing dups..')

        pipeline = [
            {"$group": {"_id": "$link", "unique_ids": {"$addToSet": "$_id"}, "count": {"$sum": 1}}},
            {"$match": {"count": {"$gte": 2}}}
        ]
        cursor = self.db.yachts.aggregate(pipeline)

        response = []
        for doc in cursor:
            del doc["unique_ids"][0]
            for unique_id in doc["unique_ids"]:
                response.append(unique_id)

        self.db.yachts.remove({"_id": {"$in": response}})

        print('removed dups.')

    def rename_field(self, oldname, newname):
        self.db.yachts.update_many({}, {'$rename': {oldname: newname}})
        print('renamed %s to %s' % (oldname, newname))

    def create_index(self):
        self.db.yachts.create_index([('link', TEXT)], unique=True)  # prevent duplicate ads next time
        print('created index')

    def drop_index(self):
        self.db.yachts.drop_index([('link', TEXT)])
        print('dropped index')

    def get_index_info(self):
        print(self.db.yachts.index_information())


if __name__ == "__main__":
    pass
