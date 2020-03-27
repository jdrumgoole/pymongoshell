#!/usr/bin/env python3

import sys
import argparse
import os
import requests

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
            if not args.database in client.list_database_names()  or \
                    not args.collection in client[args.database].list_collection_names():
                print("Retrieving file from S3")
                archive_file = requests.get("https://s3-eu-west-1.amazonaws.com/developer-advocacy-public/zipcodes.mdp.gz")

                open('zipcodes.mdp.gz', 'wb').write(archive_file.content)
                print("Restoring backup to MongoDB")
                os.system("mongorestore --drop --gzip --archive=zipcodes.mdp.gz")
            else:
                print("demo.zipcodes is already installed")

    except ConnectionFailure:
        print("Couldn't connect to server on 27017")
