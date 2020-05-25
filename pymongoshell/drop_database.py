#!/usr/bin/env python3

import argparse

import pymongo


if __name__ == "__main__":
    """
    Drop a collection.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default='mongodb://localhost:27017',
                        help="mongodb URI [default: %(default)s]")
    parser.add_argument("--database", default=None,
                        help="database name: %(default)s]")

    args = parser.parse_args()

    client = pymongo.MongoClient(host=args.host)

    if args.database in client.list_database_names():
        client.drop_database(args.database)
        print(f"Dropped: '{args.database}'")
    else:
        print(f"Database '{args.database}' does not exist")


