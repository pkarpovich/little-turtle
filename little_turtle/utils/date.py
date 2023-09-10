import locale
from datetime import datetime


def get_day_of_week(date: str) -> str:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

    date_obj = datetime.strptime(date, '%d.%m.%Y')
    return date_obj.strftime('%A').capitalize()


def validate_date(date: str) -> bool:
    try:
        datetime.strptime(date, '%d.%m.%Y')
        return True
    except ValueError:
        return False
