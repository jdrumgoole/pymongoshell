'''
Created on 12 Oct 2016

@author: jdrumgoole
'''

import pymongo
from generator_utils import coroutine

class DocEmbed( object ):
    
    def __init__(self, outerFieldName ):
        self._outerFieldName = outerFieldName
        
    def __call__(self, doc ):

        newDoc = {}
        newDoc[ self._outerFieldName ] = doc

        return newDoc
        
class DocTransform( object ):
    
    def noop(self, doc ):
        return doc
    
    def __init__(self, xformFunc = None ):
        if xformFunc is None :
            self._xformFunc = self.noop
        else:
            self._xformFunc = xformFunc
            
    def __call__(self, doc ):
        return self._xformFunc( doc )
    
class BatchWriter(object):
     
    def __init__(self, collection, transform=None, orderedWrites=False ):
         
        self._collection = collection
        self._orderedWrites = orderedWrites
        if transform is None:
            self._transform = DocTransform()
        elif type( transform ) is not DocTransform :
            raise ValueError( "transform parameter to BatchWriter is not type: %s" % type( transform ))
        else:
            self._transform = transform

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
                
            results = None
            
            bulkerCount = 0
            
            try :
                while True:
                    
                    doc = ( yield results )
                    
                    if results:
                        results = None
                        
                    
                    bulker.insert( self._transform(  doc  ))
                    bulkerCount = bulkerCount + 1 
                    if ( bulkerCount == writeLimit ):
                        results = bulker.execute()
                        if self._orderedWrites :
                            bulker = self._collection.initialize_ordered_bulk_op()
                        else:
                            bulker = self._collection.initialize_unordered_bulk_op()
                             
                        bulkerCount = 0
            except GeneratorExit :
                if ( bulkerCount > 0 ) :
                    bulker.execute() 
        except pymongo.errors.BulkWriteError as e :
            print( "Bulk write error : %s" % e.details )
            raise
