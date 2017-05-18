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

def no_op( new_name, d ) :
    _ = new_name
    return d

class BatchWriter(object):
     
    def __init__(self, collection, transformFunc=None, newDocName=None, orderedWrites=False ):
         
        self._collection = collection
        self._orderedWrites = orderedWrites
        if transformFunc is None:
            self._processFunc = no_op
        else:
            self._processFunc = transformFunc
            
        if newDocName is None:
            self._newDocName = ""
        else:
            self._newDocName = newDocName
            
        self._writeCount = 0

    def written(self):
        return self._writeCount
    
    '''
    Intialise coroutine automatically
    '''
    @coroutine 
    def bulkWrite(self, writeLimit=1000 ):
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
        

