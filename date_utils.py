from datetime import datetime

def days_between_create_date(date):
    date_format = "%Y-%m-%d %H:%M:%S"
    create_date = datetime.strptime(date, date_format)
    now = datetime.now()
    time_difference = now - create_date
    return time_difference.days