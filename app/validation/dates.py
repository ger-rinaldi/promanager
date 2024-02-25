import datetime


def is_valid_date(date_str: str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def before_today(date_str: str):
    today = datetime.date.today()
    received_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    if today < received_date:
        return False

    return True


def start_before_end(start_date: str, end_date: str) -> bool:
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

    if start_date >= end_date:
        return False

    return True


def end_after_today(end_date: str) -> bool:
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    today = datetime.date.today()

    if end_date <= today:
        return False

    return True
