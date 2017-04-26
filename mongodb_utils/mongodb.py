'''
Created on 22 Jun 2016

@author: jdrumgoole
'''

import pymongo

class MUGAlyserMongoDB( object ):
    
    def __init__(self, uri="mongodb://localhost:27017/",
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
        self._uri = pymongo.uri_parser.parse_uri( uri )
        
        if self._client.get_default_database() is None :
            self._database = self._client[ default_database ]
            
        self._collection = self._database[ default_collection ]
        self._uri_dict = pymongo.uri_parser.parse_uri( self._uri )
        
        if not "database" in self._uri_dict :
            self._url_dict[ 'database' ] = default_database
            
        if not "collection" in self._uri_dict :
            self._uri_dict[ 'collection' ] = default_collection
        
    def uri_info(self):
        return self._uri
    
    def client(self):
        return self._client
    
    def database(self):
        self._uri_dict[ 'database']
        
    def collection(self):
        self._uri_dict[ 'collection' ]
        
    def connect(self):
        
        return self._database.command("ismaster")
