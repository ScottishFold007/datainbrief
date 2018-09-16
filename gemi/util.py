import datetime


class Util:
    @staticmethod
    def get_todays_date():
        return datetime.datetime.now().date()

    @staticmethod
    def get_date_of_x_days_ago(days_ago):
        return get_todays_date() - datetime.timedelta(days=days_ago)
