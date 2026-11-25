"""Row validation: airport list loading, single-row checks, record building."""

import re 
import math 
from datetime import datetime 

DATETIME_FORMAT = "%Y-%m-%d %H:%M"

def load_airports(path: str) -> set[str]:
    airports=set()
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            code = line.strip()
            if not code or code.startswith("#"):
                continue
            airports.add(code)
    return airports

    raise NotImplementedError




def is_valid_datetime(value: str) -> bool:
    if not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}",
        value
    ):
        return False

    try:
        datetime.strptime(value, DATETIME_FORMAT)
        return True
    except ValueError:
        return False




def validate_row(fields: list[str], airports: set[str]) -> str | None:
    # 1. Check field count
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    # Strip whitespace from every field
    fields = [field.strip() for field in fields]

    flight_id, origin, destination, departure, arrival, price = fields

    # 2. Check missing fields
    if any(field == "" for field in fields):
        return "MISSING_FIELD"

    # 3. Check flight ID (ASCII letters and digits only)
    if not re.fullmatch(r"[A-Za-z0-9]{2,8}", flight_id):
        return "INVALID_FLIGHT_ID"

    # 4. Check origin
    if not re.fullmatch(r"[A-Z]{3}", origin):
        return "INVALID_ORIGIN"

    if origin not in airports:
        return "INVALID_ORIGIN"

    # 5. Check destination
    if not re.fullmatch(r"[A-Z]{3}", destination):
        return "INVALID_DESTINATION"

    if destination not in airports:
        return "INVALID_DESTINATION"

    # 6. Check that origin and destination differ
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    # 7. Check departure datetime
    if not is_valid_datetime(departure):
        return "INVALID_DEPARTURE"

    # 8. Check arrival datetime
    if not is_valid_datetime(arrival):
        return "INVALID_ARRIVAL"

    departure_time = datetime.strptime(
        departure, DATETIME_FORMAT
    )
    arrival_time = datetime.strptime(
        arrival, DATETIME_FORMAT
    )

    # 9. Arrival must be after departure
    if arrival_time <= departure_time:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    # 10. Check price conversion and finiteness
    try:
        price_value = float(price)
    except (ValueError, OverflowError):
        return "INVALID_PRICE"

    if not math.isfinite(price_value):
        return "INVALID_PRICE"

    # 11. Price must be positive
    if price_value <= 0:
        return "NON_POSITIVE_PRICE"

    return None
    
    raise NotImplementedError


def to_record(fields: list[str]) -> dict:
    fields = [field.strip() for field in fields]

    return {
        "flight_id": fields[0],
        "origin": fields[1],
        "destination": fields[2],
        "departure_datetime": fields[3],
        "arrival_datetime": fields[4],
        "price": float(fields[5])
    }

    raise NotImplementedError
