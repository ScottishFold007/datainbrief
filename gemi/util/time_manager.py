from datetime import datetime

date_now = datetime.now().date().isoformat()


def str_to_date(str):
    return datetime.strptime(str, '%Y-%m-%d').date()
