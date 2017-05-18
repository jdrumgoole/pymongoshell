'''
Created on 22 Jun 2016

@author: jdrumgoole
'''

import pymongo

class MongoDB( object ):
    
    def __init__(self, uri="mongodb://localhost:27017/test",
                 default_port = 20717,
                 default_database = "test",
                 default_collection = "test" ):      

        '''
        Example URL 
        
        mongodb://<username>:<password>@<host list>/database?<args>
        
        "mongodb://jdrumgoole:PASSWORD@mugalyser-shard-00-00-ffp4c.mongodb.net:27017,
        mugalyser-shard-00-01-ffp4c.mongodb.net:27017,
        mugalyser-shard-00-02-ffp4c.mongodb.net:27017/admin?ssl=true&replicaSet=MUGAlyser-shard-0&authSource=admin"
        
        '''
        
        self._client = pymongo.MongoClient( uri )
        self._uri_dict = pymongo.uri_parser.parse_uri( uri )
        
        if self._client.get_default_database() is None :
            self._database = self._client[ default_database ]
        else:
            self._database = self._client.get_default_database()
            
        if not "collection" in self._uri_dict:
            self._collection = self._database[ default_collection ]
        else:
            self._collection = self._database[ self._uri_dict[ "collection"]]
        
    def uri_info(self):
        return self._uri_dict
    
    def client(self):
        return self._client
    
    def database(self):
        return self._database
        
    def collection(self, collection_name ):
        return self._database[ collection_name ]
        
    def connect(self):
        
        return self._database.command("ismaster")
