from datetime import datetime, timedelta

todays_date = datetime.now().date().isoformat()

date_of_x_days_ago = lambda x: (datetime.now().date() - timedelta(days=x)).isoformat()

str_to_date = lambda str: datetime.strptime(str, '%Y-%m-%d').date()
