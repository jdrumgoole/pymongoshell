'''

Use a generator function to recieve data from the send command. Accumulate docs until
writeLimit is reached and then bulkexecute writes. Keep a count of write ops in
writeCount.

Created on 12 Oct 2016

@author: jdrumgoole
'''

import pymongo
import bson

from mongodb_utils.generator_utils import coroutine
from pydoc import doc

def no_op( new_name, d ) :
    _ = new_name
    return d

def feedback_nop( doc ):
    _ = doc
    print( "." )

class Pipeline( object ):
       
    def actor(self, doc ):
        return doc
    
    @coroutine  
    def pour(self, destination ):
        while True:
            doc = (yield)
            destination.send( self.actor( doc ))

class Sink( object ):
        
    def ender( self, doc  ):
        pass 
    
    @coroutine
    def drain( self ):
        while True:
            doc = (yield)
            self.ender( doc )
            
class Bulk_Writer(object):
    '''
    Bulk_Writer
    ==================
    Bulk_Writer is a wrapper class for the bulk_write operation in mongodb. It allows user
    to send (using generator send operations) write and update operations to MongoDB which accumulates 
    them up a batch_size threshold. Once the threshold is met the operations are committed to the server.
    
    In the event that the generator is destroy before completing its write operations then the generator exit
    exception that is called will force remaining writes to be completed.
    '''
     
    def __init__(self, collection, transformFunc=None, newDocName=None, feedback=None):
         
        self._collection = collection
        self._orderedWrites = False
        if transformFunc is None:
            self._processFunc = no_op
        else:
            self._processFunc = transformFunc
            
        if newDocName is None:
            self._newDocName = ""
        else:
            self._newDocName = newDocName
            
        self._writeCount = 0

        self._feedback = feedback
        
    def written(self):
        return self._writeCount
    
    '''
    Intialise coroutine automatically
    '''
    @coroutine 
    def __call__(self, writeLimit=1000 ):
        bulker = None
        try : 
            if self._orderedWrites :
                bulker = self._collection.initialize_ordered_bulk_op()
            else:
                bulker = self._collection.initialize_unordered_bulk_op()
                
            bulkerCount = 0
            
            try :
                while True:
                    doc = (yield)
                    if self._feedback :
                        self._feedback( doc )
                    #pprint.pprint( doc )) 
                    bulker.insert( self._processFunc(  self._newDocName, doc  ))
                    bulkerCount = bulkerCount + 1 
                    if ( bulkerCount == writeLimit ):
                        result = bulker.execute()
                        self._writeCount = self._writeCount + result['nInserted' ]
                        if self._orderedWrites :
                            bulker = self._collection.initialize_ordered_bulk_op()
                        else:
                            bulker = self._collection.initialize_unordered_bulk_op()
                             
                        bulkerCount = 0
            except GeneratorExit :
                if ( bulkerCount > 0 ) :
                    result = bulker.execute() 
                    self._writeCount = self._writeCount + result['nInserted' ]
            except bson.errors.InvalidDocument as e:
                print( "Invalid Document" )
                print( "bson.errors.InvalidDocument: %s" % e )
                raise
            
        except pymongo.errors.BulkWriteError as e :
            print( "Bulk write error : %s" % e.details )
            raise
        

