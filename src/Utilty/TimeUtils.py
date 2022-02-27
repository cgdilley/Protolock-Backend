
from datetime import datetime

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def stringify_date(d: datetime) -> str:
    iso = d.strftime(DATE_FORMAT)
    decimal_pos = iso.rfind(".")
    seconds_fraction = iso[decimal_pos + 1:-1]
    millis = seconds_fraction.rjust(3, "0")[:3]
    return iso[:decimal_pos + 1] + millis + "Z"


def parse_date(s: str) -> datetime:
    return datetime.strptime(s, DATE_FORMAT)
