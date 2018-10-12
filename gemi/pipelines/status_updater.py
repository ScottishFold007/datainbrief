# project packages
from gemi.database import db, collection_name
from gemi.util.time_manager import date_now


class StatusUpdater(object):

    @staticmethod
    def set_initial_status():
        # set all as not updated first
        db[collection_name].update_many(
            {"dates.last_updated": {"$lt": date_now}},  # select unsold items
            {
                '$set': {'status.updated': False}
            }
        )

    @staticmethod
    def record_removed_items():
        # prepare updates
        new_status = {
            'status.removed': True,
            'status.active': False,
            'status.sale_pending': False,
            'dates.removed': date_now
        }

        # get untouched items and update
        db[collection_name].update_many(
            {'status.updated': False},
            {'$set': new_status}
        )
