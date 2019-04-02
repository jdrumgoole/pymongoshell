#!/usr/bin/env python3

import sys
import argparse

import pymongo
from pymongo.errors import ConnectionFailure


if __name__ == "__main__":
    """
    Check for existence of database collection. Defaults to demo.zipcodes.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default='mongodb://localhost:27017',
                        help="mongodb URI [default: %(default)s]")
    parser.add_argument("--database", default='demo',
                        help="database name: %(default)s]")
    parser.add_argument("--collection", default='zipcodes',
                        help="collection name: %(default)s]")

    args = parser.parse_args()

    client = pymongo.MongoClient(host=args.host)

    exit_code=0
    try:
        # The ismaster command is cheap and does not require auth.

        doc = client.admin.command('ismaster')
        if doc:
            if args.database in client.list_database_names():
                if args.collection in client[args.database].list_collection_names():
                    #print("'{args.collection}' exists")
                    exit_code=0
                else:
                    #print("'{args.database}.{args.collection}' doesn't exist")
                    exit_code=1

            else:
                #print(f"'{args.database}' doesn't exist")
                exit_code=1

        sys.exit(exit_code)

    except ConnectionFailure:
        sys.exit(1)
