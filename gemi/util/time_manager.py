from datetime import datetime

date_now = datetime.now().date().isoformat()


def get_date_of_x_days_ago(days_ago):
    return datetime.now().date() - datetime.timedelta(days=days_ago)


date_yesterday = get_date_of_x_days_ago(1).isoformat()


def str_to_date(str):
    return datetime.strptime(str, '%Y-%m-%d').date()
