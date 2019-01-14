"""
Author : joe@joedrumgoole.com

MPing : Ping a MongoDB server with an is_master command.

"""

import pymongo
from pymongo.errors import ConnectionFailure
from datetime import datetime
import pprint
import sys

if __name__ == "__main__":

    arg = None

    if len(sys.argv) > 1:
        arg = sys.argv[1]

    client = pymongo.MongoClient(host=arg)
    try:
        # The ismaster command is cheap and does not require auth.
        start = datetime.utcnow()
        doc = client.admin.command('ismaster')
        end = datetime.utcnow()

        duration = end - start
        print(f"ismaster took : {duration}")
        pprint.pprint(doc)

    except ConnectionFailure:
        end = datetime.utcnow()
        print("Server not available")
        duration = end - start
        print(f"connection failure took : {duration}")
