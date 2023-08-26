import locale
from datetime import datetime


def get_day_of_week(date: str) -> str:
    locale.setlocale(locale.LC_TIME, 'ru_RU')

    date_obj = datetime.strptime(date, '%d.%m.%Y')
    return date_obj.strftime('%A').capitalize()