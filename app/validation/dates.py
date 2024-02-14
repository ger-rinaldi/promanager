import datetime


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
