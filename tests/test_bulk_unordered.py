'''
Created on 10 Sep 2017

@author: jdrumgoole
'''
import pymongo
if __name__ == "__main__":
    
    client = pymongo.MongoClient()
    db = client[ "test"]
    col = db[ "test"]
    bulker = col.initialize_unordered_bulk_op()