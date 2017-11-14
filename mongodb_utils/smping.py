# How to ping a MongoDB Server
import pymongo
from pymongo.errors import ConnectionFailure
client = pymongo.MongoClient()
try:
    print(client.admin.command('ismaster'))
except ConnectionFailure:
    print("no server")
