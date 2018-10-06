from datetime import datetime


class TimeManager:
    @staticmethod
    def get_todays_date():
        return datetime.now().date()

    @staticmethod
    def get_date_of_x_days_ago(days_ago):
        return datetime.now().date() - datetime.timedelta(days=days_ago)

    @staticmethod
    def str_to_date(str):
        return datetime.strptime(str, '%Y-%m-%d').date()
