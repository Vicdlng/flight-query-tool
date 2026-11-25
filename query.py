
from datetime import datetime
import math

from validator import is_valid_datetime


RECORD_KEYS = {
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price"
}

ALLOWED_KEYS = RECORD_KEYS | {
    "min_price",
    "sort_by",
    "order",
    "limit"
}


def valid_query(query: dict) -> bool:
    """Check whether a query follows all query rules."""

    if not isinstance(query, dict):
        return False

    # Unknown keys
    if not set(query.keys()).issubset(ALLOWED_KEYS):
        return False

    # Exact-match string fields
    for key in ("flight_id", "origin", "destination"):
        if key in query and not isinstance(query[key], str):
            return False

    # Datetime fields
    for key in ("departure_datetime", "arrival_datetime"):
        if key in query:
            if not isinstance(query[key], str):
                return False

            if not is_valid_datetime(query[key]):
                return False

    # Numeric fields (bool is not accepted)
    for key in ("price", "min_price"):
        if key in query:
            value = query[key]

            if isinstance(value, bool):
                return False

            if not isinstance(value, (int, float)):
                return False

            if not math.isfinite(value):
                return False

    # Sorting
    if "sort_by" in query:
        if not isinstance(query["sort_by"], str):
            return False

        if query["sort_by"] not in RECORD_KEYS:
            return False

    # Order
    if "order" in query:
        if "sort_by" not in query:
            return False

        if query["order"] not in ("asc", "desc"):
            return False

    # Limit
    if "limit" in query:
        value = query["limit"]

        if isinstance(value, bool):
            return False

        if not isinstance(value, int):
            return False

        if value < 0:
            return False

    return True


def run_query(db: list[dict], query: dict) -> dict:
    """Execute one query and return its response."""

    if not valid_query(query):
        return {
            "query": query,
            "error": "INVALID_QUERY",
            "matches": []
        }

    matches = []

    for flight in db:

        # Exact-match conditions
        if "flight_id" in query:
            if flight["flight_id"] != query["flight_id"]:
                continue

        if "origin" in query:
            if flight["origin"] != query["origin"]:
                continue

        if "destination" in query:
            if flight["destination"] != query["destination"]:
                continue

        # Departure must be at or after the requested time
        if "departure_datetime" in query:
            flight_time = datetime.strptime(
                flight["departure_datetime"], "%Y-%m-%d %H:%M"
            )
            requested_time = datetime.strptime(
                query["departure_datetime"], "%Y-%m-%d %H:%M"
            )

            if flight_time < requested_time:
                continue

        # Arrival must be at or before the requested time
        if "arrival_datetime" in query:
            flight_time = datetime.strptime(
                flight["arrival_datetime"], "%Y-%m-%d %H:%M"
            )
            requested_time = datetime.strptime(
                query["arrival_datetime"], "%Y-%m-%d %H:%M"
            )

            if flight_time > requested_time:
                continue

        # Maximum price
        if "price" in query:
            if flight["price"] > query["price"]:
                continue

        # Minimum price
        if "min_price" in query:
            if flight["price"] < query["min_price"]:
                continue

        matches.append(flight)

    # Sorting
    if "sort_by" in query:
        sort_key = query["sort_by"]
        reverse = query.get("order", "asc") == "desc"

        matches = sorted(
            matches,
            key=lambda flight: flight[sort_key],
            reverse=reverse
        )

    # Limit
    if "limit" in query:
        matches = matches[:query["limit"]]

    return {
        "query": query,
        "matches": matches
    }


def run_queries(
    db: list[dict],
    queries: dict | list
) -> list[dict]:

    if isinstance(queries, dict):
        queries = [queries]

    if not isinstance(queries, list):
        return [{
            "query": queries,
            "error": "INVALID_QUERY",
            "matches": []
        }]

    return [
        run_query(db, query)
        for query in queries
    ]
