
import argparse
import json
import logging
import os
import sys
import csv 

from datetime import datetime
from validator import load_airports
from csv_loader import parse_files
from query import run_queries

STUDENT_ID = "260AMB053"
FIRST_NAME = "VICTORIA"
LAST_NAME = "DELONG"


def create_parser():
    parser = argparse.ArgumentParser(
        description="Flight Query Tool"
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", metavar="FILE")
    source.add_argument("-d", metavar="FOLDER")
    source.add_argument("-j", metavar="FILE")
    parser.add_argument("-a", metavar="FILE")
    parser.add_argument("-o", default=None, metavar="FILE")
    parser.add_argument("-q", metavar="FILE")
    parser.add_argument("-r", default=".", metavar="FOLDER")
    return parser


def main(argv: list[str] | None = None) -> int:
    logger=None
    handler=None
    parser = create_parser()
    args = parser.parse_args(argv)


    # Usage checks
    if args.j and args.o is not None:
        parser.error("-o cannot be used with -j")
    if args.i or args.d:
        if not args.a:
            parser.error("-a is required with -i or -d")
        if args.o is None:
            args.o = "db.json"

    




    try:
        # OPTION 1: LOAD EXISTING JSON DATABASE

        if args.j:
            with open(args.j, "r", encoding="utf-8") as file:
                db = json.load(file)
            if not isinstance(db, list):
                raise ValueError("Database must be a JSON array")
            if not all(isinstance(record, dict) for record in db):
                raise ValueError("Database must contain objects")

        # OPTION 2: PARSE CSV FILES

        else:

            if args.i:
                paths = [args.i]

            else:
                if not os.path.isdir(args.d):
                    raise FileNotFoundError(
                        f"Folder not found: {args.d}"
                    )

                paths = sorted(
                    os.path.join(args.d, filename)
                    for filename in os.listdir(args.d)
                    if filename.endswith(".csv")
                    and os.path.isfile(
                        os.path.join(args.d, filename)
                    )
                )

                if not paths:
                    raise ValueError(
                        "No CSV files found in folder"
                    )

            airports = load_airports(args.a)
            log_path = os.path.join(
                os.path.dirname(os.path.abspath(args.o)),
                "errors.log"
            )

            logger = logging.getLogger("flight_parser")
            logger.setLevel(logging.INFO)

            handler = logging.FileHandler(
                log_path,
                mode="w",
                encoding="utf-8"
            )

            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                )
            )

            logger.addHandler(handler)
            db, errors = parse_files(paths, airports)
            with open(args.o, "w", encoding="utf-8") as file:
                json.dump(db, file, indent=2)
            for error in errors:
                logger.warning(error)

        # OPTION 3: EXECUTE QUERIES

        if args.q:
            with open(args.q, "r", encoding="utf-8") as file:
                queries = json.load(file)
            if isinstance(queries, dict):
                pass
            elif isinstance(queries, list):
                if not all(
                    isinstance(query, dict)
                    for query in queries
                ):
                    raise ValueError(
                        "Query file must contain query objects"
                    )

            else:
                raise ValueError(
                    "Query file must contain an object or array"
                )
            responses = run_queries(db, queries)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            response_name = (
                f"response_{STUDENT_ID}_{FIRST_NAME}_"
                f"{LAST_NAME}_{timestamp}.json"
            )
            response_path = os.path.join(
                args.r,
                response_name
            )
            with open(
                response_path, "w", encoding="utf-8"
            ) as file:
                json.dump(responses, file, indent=2)

        print("Flight Query Tool completed successfully.")
        return 0

    except (OSError, json.JSONDecodeError, ValueError, csv.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    finally:
        if logger is not None and handler is not None:
            logger.removeHandler(handler)
            handler.close()


if __name__ == "__main__":
    sys.exit(main())



