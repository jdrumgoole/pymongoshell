#!/usr/bin/env python3

import sys
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
    parser.add_argument("--collection", default=None,
                        help="collection name: %(default)s]")


    args = parser.parse_args()

    client = pymongo.MongoClient(host=args.host)

    if args.database in client.list_database_names():
        if args.collection in client[args.database].list_collection_names():
            client[args.database].drop_collection(args.collection)
            print(f"Dropped: '{args.database}.{args.collection}'")
        else:
            print(f"Collection '{args.database}.{args.collection}' does not exist")
    else:
        print(f"Database '{args.database}' does not exist")

