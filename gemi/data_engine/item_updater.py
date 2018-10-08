
class ItemUpdater(object):
    @staticmethod
    def is_already_updated(item, todays_date):
        last_updated = TimeManager.str_to_date(item['dates']['last-updated'])
        if last_updated == todays_date:  # already updated today
            print(last_updated.isoformat(), 'already updated today')
            return True

    def update_already_existing_item(self, item, price, sale_pending, todays_date):
        updates = dict()

        if not item:
            return True

        # check last update
        if self.is_already_updated(item, todays_date):
            return True

        # check the price
        last_price = item['price']

        if last_price != price:
            updates['status.price_changed'] = True
            updates['price'] = Cleaner.clean_price(price)
            updates['dates.price_changed'] = todays_date

        # check sale status
        if sale_pending:
            updates['status.sale_pending'] = True
            updates['dates.sale_pending'] = todays_date

        updates['updated'] = True
        updates['status.removed'] = False
        updates['dates.last-updated'] = todays_date

        print('updated: ', updates)

        return updates
