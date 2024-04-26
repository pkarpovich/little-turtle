from datetime import datetime


def get_day_of_week(date: str) -> str:
    date_obj = datetime.strptime(date, "%d.%m.%Y")
    return date_obj.strftime("%A").capitalize()


def validate_date(date: str) -> bool:
    try:
        datetime.strptime(date, "%d.%m.%Y")
        return True
    except (ValueError, TypeError):
        return False


def parse_date(date: str) -> datetime | None:
    try:
        return datetime.strptime(date, "%d.%m.%Y")
    except (ValueError, IndexError):
        return None
