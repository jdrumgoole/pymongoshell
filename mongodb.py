'''
Created on 22 Jun 2016

@author: jdrumgoole
'''

import pymongo

class MongoDB( object ):
    
    def __init__(self, uri="mongodb://localhost:27017", databaseName="TEST", connect=True):
        
        '''
        Example URL 
        
        mongodb://<username>:<password>@<host list>/database?<args>
        
        "mongodb://jdrumgoole:PASSWORD@mugalyser-shard-00-00-ffp4c.mongodb.net:27017,
        mugalyser-shard-00-01-ffp4c.mongodb.net:27017,
        mugalyser-shard-00-02-ffp4c.mongodb.net:27017/admin?ssl=true&replicaSet=MUGAlyser-shard-0&authSource=admin"
        
        '''
        
        self._uri = uri

        self._client = None
        self._database_name   = databaseName
        self._client = pymongo.MongoClient( host=self._uri )
        self._database = self._client[ self._database_name]
        if connect:
            self.ismaster()
            
    def ismaster(self):
        return self._database.command( "ismaster" )
#           
    def client(self):
        return self._client
    
    def database(self) :
        return self._database
    
    def make_collection(self, collection_name ):
        return self._database[ collection_name ]

    