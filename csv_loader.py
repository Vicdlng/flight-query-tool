
import csv
import os

from validator import validate_row, to_record


def parse_files(
    paths: list[str],
    airports: set[str]
) -> tuple[list[dict], list[str]]:

    valid_records = []
    errors = []

    # Keep track of valid flight ID and departure combinations
    seen_flights = set()

    for path in paths:
        filename = os.path.basename(path)

        with open(path, "r", encoding="utf-8", newline="") as file:

            for line_number, line in enumerate(file, start=1):

                # Skip the header
                if line_number == 1:
                    continue

                # Skip blank lines
                if not line.strip():
                    continue

                # Skip comments
                if line.lstrip().startswith("#"):
                    continue

                # Parse CSV using the csv module
                reader = csv.reader([line])

                try:
                    fields = next(reader)
                except StopIteration:
                    continue

                # Remove whitespace
                fields = [field.strip() for field in fields]

                # Validate row
                error_code = validate_row(fields, airports)

                if error_code is not None:
                    original_line = line.rstrip("\r\n")

                    errors.append(
                        f"{filename}:{line_number}: "
                        f"{error_code} | {original_line}"
                    )
                    continue

                # Check duplicates only after validation
                flight_key = (
                    fields[0],
                    fields[3]
                )

                if flight_key in seen_flights:
                    original_line = line.rstrip("\r\n")

                    errors.append(
                        f"{filename}:{line_number}: "
                        f"DUPLICATE_FLIGHT | {original_line}"
                    )
                    continue

                seen_flights.add(flight_key)

                valid_records.append(to_record(fields))

    return valid_records, errors
