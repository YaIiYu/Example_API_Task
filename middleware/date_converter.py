from datetime import date
from babel.dates import format_date
import locale
import re
import datetime


def convert(date, short=False, locale_code='en'):
    raw_result = re.compile(r'^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})$').search(date).groups()
    month = int(raw_result[1])
    if not (1 <= month <= 12):
        raise ValueError("1 <= month <= 12")
    try:
        locale.setlocale(locale.LC_TIME, locale_code)
    except locale.Error:
        locale.setlocale(locale.LC_TIME, 'en')

    test_date = datetime.date(year=int(raw_result[0]), month=month, day=int(raw_result[2]))
    res_time = f", {raw_result[3]}:{raw_result[4]}"
    result = "dd MMM. YYYY"+res_time if short else "dd MMMM YYYY"+res_time

    return format_date(test_date, result, locale=locale_code)

if __name__ == "__main__":
    print(convert("2024-10-23 19:26", True))
